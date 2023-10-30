from decimal import Decimal
import pytest

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def mock_update_chain(mocker):
    return mocker.patch("apps.orders.services.purchase_creator.chain")


@pytest.fixture
def mock_rebuild_tags(mocker):
    return mocker.patch("apps.users.tasks.rebuild_tags.si")


@pytest.fixture
def rebuild_tags(mocker):
    return mocker.patch("apps.users.tasks.rebuild_tags.delay")


@pytest.fixture
def mock_push_customer(mocker):
    return mocker.patch("apps.amocrm.tasks.push_user.si")


@pytest.fixture
def mock_push_order(mocker):
    return mocker.patch("apps.amocrm.tasks.push_order.si")


def get_order():
    return Order.objects.last()


def test_order(call_purchase, course):
    call_purchase()

    placed = get_order()

    assert placed.item == course
    assert placed.price == Decimal("1900.00")
    assert not hasattr(placed, "study")  # Study record is not created yet, because order is not paid


def test_user(call_purchase):
    call_purchase()

    placed = get_order()

    assert placed.user.first_name == "Забой"
    assert placed.user.last_name == "Шахтёров"
    assert placed.user.email == "zaboy@gmail.com"


@pytest.mark.parametrize(
    ("wants_to_subscribe", "should_be_subscribed"),
    [
        ("True", True),
        ("true", True),
        ("1", True),
        (1, True),
        ("False", False),
        ("false", False),
        ("0", False),
        (0, False),
    ],
)
def test_update_chain_called_with_correct_args(
    call_purchase, wants_to_subscribe, should_be_subscribed, mock_update_chain, mock_rebuild_tags, mock_push_customer, mock_push_order, settings
):
    settings.AMOCRM_BASE_URL = "https://mamo.amo.criminal"

    call_purchase(subscribe=wants_to_subscribe)

    placed = get_order()
    placed.user.refresh_from_db()

    mock_update_chain.assert_called_once()
    mock_rebuild_tags.assert_called_once_with(student_id=placed.user.id, subscribe=should_be_subscribed)
    mock_push_customer.assert_called_once_with(user_id=placed.user.id)
    mock_push_order.assert_called_once_with(order_id=placed.id)


def test_by_default_user_is_not_subscribed(call_purchase):
    call_purchase()

    placed = get_order()

    assert placed.user.subscribed is False


def test_redirect(call_purchase):
    response = call_purchase(as_response=True)

    assert response.status_code == 302
    assert response["Location"] == "https://bank.test/pay/"


def test_custom_success_url(call_purchase, bank):
    call_purchase(success_url="https://ok.true/yes")
    assert bank.call_args[1]["success_url"] == "https://ok.true/yes"


def test_invalid(client):
    response = client.post("/api/v2/courses/ruloning-oboev/purchase/", {})

    assert response.status_code == 400
