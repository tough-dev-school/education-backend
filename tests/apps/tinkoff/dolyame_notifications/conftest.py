import pytest

from core.test.api_client import DRFClient


@pytest.fixture(autouse=True)
def _credentials(settings):
    settings.DOLYAME_LOGIN = "root"
    settings.DOLYAME_PASSWORD = "l0ve"
    settings.DOLYAME_CERTIFICATE_PATH = "tests/apps/tinkoff/.fixtures/testing.pem"


@pytest.fixture
def api():
    return DRFClient(anon=True, HTTP_X_FORWARDED_FOR="91.194.226.100, 10.0.0.1")


@pytest.fixture
def fake_client():
    return DRFClient(anon=True, HTTP_X_FORWARDED_FOR="8.8.8.8, 10.0.0.1")


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


@pytest.fixture
def payment_schedule() -> list[dict]:
    return [
        {
            "payment_date": "2020-11-20",
            "amount": 2500.14,
            "status": "hold",
        },
        {
            "payment_date": "2020-12-04",
            "amount": 2500.14,
            "status": "scheduled",
        },
        {
            "payment_date": "2020-12-18",
            "amount": 2500.14,
            "status": "scheduled",
        },
        {
            "payment_date": "2021-01-1",
            "amount": 2500.14,
            "status": "scheduled",
        },
    ]
