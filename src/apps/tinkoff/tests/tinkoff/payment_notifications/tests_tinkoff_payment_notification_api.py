from decimal import Decimal

import pytest

from apps.orders.models import Order
from apps.tinkoff.exceptions import TinkoffPaymentNotificationInvalidToken
from apps.tinkoff.models import PaymentNotification

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def order(order):
    """Manualy setting order id to avoid confusion with token regeneration"""
    Order.objects.filter(id=order.id).update(id=201709)

    return Order.objects.get(id=201709)


@pytest.fixture
def req(order):
    return {
        "TerminalKey": "1321054611234DEMO",
        "OrderId": order.slug,
        "Success": True,
        "Status": "AUTHORIZED",
        "PaymentId": 8742591,
        "ErrorCode": 0,
        "Amount": 9855,
        "RebillId": 101709,
        "CardId": 322264,
        "Pan": "430000******0777",
        "Token": "b906d28e76c6428e37b25fcf86c0adc52c63d503013fdd632e300593d165766b",
        "ExpDate": "1122",
    }


@pytest.mark.usefixtures("_disable_token_validation")
def test_success_creation(anon, req, order):
    anon.post("/api/v2/banking/tinkoff-notifications/", req, expected_status_code=200)

    instance = PaymentNotification.objects.last()

    assert instance.terminal_key == "1321054611234DEMO"
    assert instance.order == order
    assert instance.success is True
    assert instance.status == "AUTHORIZED"
    assert instance.payment_id == 8742591
    assert instance.error_code == "0"
    assert instance.amount == Decimal("98.55")
    assert instance.rebill_id == 101709
    assert instance.card_id == "322264"
    assert instance.pan == "430000******0777"
    assert instance.data is None
    assert instance.exp_date == "1122"


@pytest.mark.usefixtures("_disable_token_validation")
def test_success_response(anon, req):
    got = anon.post("/api/v2/banking/tinkoff-notifications/", req, expected_status_code=200)

    assert got == "OK"


@pytest.mark.parametrize("card_id", ["", None])
@pytest.mark.usefixtures("_disable_token_validation")
def test_empty_card_id(anon, req, card_id):
    req["CardId"] = card_id

    anon.post("/api/v2/banking/tinkoff-notifications/", req, expected_status_code=200)


def test_creation_with_invalid_token(anon, req):
    req["Token"] = "1nv4l1d"

    with pytest.raises(TinkoffPaymentNotificationInvalidToken):
        anon.post("/api/v2/banking/tinkoff-notifications/", req, expected_status_code=200)
