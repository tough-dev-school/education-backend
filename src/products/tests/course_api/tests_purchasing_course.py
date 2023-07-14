from decimal import Decimal
import pytest

from orders.models import Order

pytestmark = [pytest.mark.django_db]


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
def test_user_auto_subscription(call_purchase, wants_to_subscribe, should_be_subscribed, rebuild_tags):
    call_purchase(subscribe=wants_to_subscribe)

    placed = get_order()
    placed.user.refresh_from_db()

    assert rebuild_tags.called is should_be_subscribed


def test_subscription_tags(call_purchase, rebuild_tags):
    call_purchase(subscribe=True)

    placed = get_order()

    rebuild_tags.assert_called_once_with(placed.user.id)


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
