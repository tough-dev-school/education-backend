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
    return factory.order(bank_id="dolyame")


@pytest.fixture(autouse=True)
def _disable_dolyame_authn(mocker):
    mocker.patch("tinkoff.api.permissions.DolyameNetmaskPermission.has_permission", return_value=True)


@pytest.fixture
def notification(order):
    def _notification(status: str, **kwargs):
        return {
            "id": order.slug,
            "status": status,
            "amount": 10000.56,
            "residual_amount": 7500.42,
            "demo": False,
            "client_info": {
                "first_name": "Иван",
                "last_name": "И.",
                "middle_name": "Иванович",
                "email": "t**@y*.ru",
                "phone": "+79003332211",
                "birthdate": "1997-05-15",
            },
            **kwargs,
        }

    return _notification


def test_ok(api, order, notification):
    api.post(
        "/api/v2/banking/dolyame-notifications/",
        notification(
            status="completed",
        ),
        expected_status_code=200,
    )

    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone(timedelta(hours=1)))


@pytest.mark.parametrize("status", ["approved", "rejected"])
def test_wr0ng_status(api, order, notification, status):
    api.post(
        "/api/v2/banking/dolyame-notifications/",
        notification(
            status=status,
        ),
        expected_status_code=200,
    )

    order.refresh_from_db()

    assert order.paid is None
