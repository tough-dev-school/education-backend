from datetime import datetime
from datetime import timedelta
from datetime import timezone
import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30+01:00"),
]


@pytest.fixture
def order(factory):
    return factory.order(bank_id="tinkoff_bank")


@pytest.fixture(autouse=True)
def _tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = "testDEMO"
    settings.TINKOFF_TERMINAL_PASSWORD = "Dfsfh56dgKl"


@pytest.fixture(autouse=True)
def disable_token_validation(mocker):
    return mocker.patch("apps.tinkoff.api.views.TinkoffNotificationsTokenValidator.__call__", return_value=True)


@pytest.fixture
def bank_data():
    return lambda **kwargs: {
        "TerminalKey": "1321054611234DEMO",
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
        **kwargs,
    }


def test_ok(anon, order, bank_data):
    anon.post(
        "/api/v2/banking/tinkoff-notifications/",
        bank_data(Status="CONFIRMED", OrderId=order.slug),
        expected_status_code=200,
    )

    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone(timedelta(hours=1)))


@pytest.mark.parametrize("status", ["AUTHORIZED", "CANCELLED"])
def test_wrong_status(anon, order, bank_data, status):
    anon.post(
        "/api/v2/banking/tinkoff-notifications/",
        bank_data(Status=status, OrderId=order.slug),
        expected_status_code=200,
    )

    order.refresh_from_db()

    assert order.paid is None
