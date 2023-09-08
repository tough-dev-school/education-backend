import pytest

from respx import MockRouter

from banking.atol import auth
from banking.atol import exceptions

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def fetch(mocker):
    return mocker.patch("banking.atol.auth.fetch", return_value="secret")


def test_ok(respx_mock: MockRouter):
    respx_mock.route(url="https://online.atol.ru/possystem/v4/getToken").respond(
        json={
            "error": None,
            "token": "__mocked",
            "timestamp": "30.11.2017 17:58:53",  # this the real timestamp from official docs
        }
    )

    assert auth.get_atol_token() == "__mocked"


@pytest.mark.parametrize("status_code", [200, 400, 500])
def test_400(respx_mock: MockRouter, status_code):
    respx_mock.route(url="https://online.atol.ru/possystem/v4/getToken").respond(
        status_code=status_code,
        json={
            "error": {
                "error_id": "4475d6d8d-844d-4d05-aa8b-e3dbdf3defd5",
                "code": 12,
                "text": "Sorry",
                "type": "system",
            },
            "timestamp": "30.11.2017 17:58:53",
        },
    )

    with pytest.raises(exceptions.AtolAuthError, match="Sorry"):
        auth.get_atol_token()


def test_cache(fetch):
    for _ in range(3):
        auth.get_atol_token()

    fetch.assert_called_once()
