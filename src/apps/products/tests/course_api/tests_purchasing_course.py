import json
from decimal import Decimal

import pytest

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def rebuild_tags(mocker):
    return mocker.patch("apps.users.tasks.rebuild_tags.delay")


@pytest.fixture
def push_customer_to_amocrm(mocker):
    return mocker.patch("apps.amocrm.tasks.push_user.si")


@pytest.fixture
def update_dashamail(mocker):
    return mocker.patch("apps.dashamail.tasks.update_subscription.apply_async")


@pytest.fixture
def push_order_to_amocrm(mocker):
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


def test_analytics_metadata(call_purchase):
    call_purchase(
        analytics=json.dumps(
            {
                "test_param": "test_value",
                "empty": None,
            }
        )
    )
    placed = get_order()

    assert placed.analytics["test_param"] == "test_value"
    assert placed.analytics["empty"] is None


def test_order_creation_does_not_fail_with_nonexistant_params(call_purchase):
    """Need this test cuz we may alter frontend request without corresponding changes on backend"""
    call_purchase(
        {
            "nonexistant": None,
            "Петрович": "Львович",
        }
    )

    assert get_order() is not None


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
def test_user_is_subscribed_to_dashamail_if_allowed(call_purchase, wants_to_subscribe, should_be_subscribed, update_dashamail):
    call_purchase(subscribe=wants_to_subscribe)

    assert (update_dashamail.call_count == 1) is should_be_subscribed


def test_integrations_are_updated(call_purchase, rebuild_tags, push_customer_to_amocrm, push_order_to_amocrm, settings):
    settings.AMOCRM_BASE_URL = "https://mamo.amo.criminal"

    call_purchase()

    placed = get_order()
    placed.user.refresh_from_db()

    rebuild_tags.assert_called_once_with(student_id=placed.user.id)
    push_customer_to_amocrm.assert_called_once_with(user_id=placed.user.id)
    push_order_to_amocrm.assert_called_once_with(order_id=placed.id)


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
