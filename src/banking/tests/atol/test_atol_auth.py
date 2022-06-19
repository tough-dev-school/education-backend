import pytest
from pytest_httpx import HTTPXMock

from banking.atol import auth, exceptions

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def fetch(mocker):
    return mocker.patch('banking.atol.auth.fetch', return_value='secret')


def test_ok(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url='https://online.atol.ru/possystem/v4/getToken',
        json={
            'error': None,
            'token': '__mocked',
            'timestamp': '30.11.2017 17:58:53',  # this the real timestamp from official docs
        },
    )

    assert auth.get_atol_token() == '__mocked'


@pytest.mark.parametrize('status_code', [200, 400, 500])
def test_400(httpx_mock: HTTPXMock, status_code):
    httpx_mock.add_response(
        url='https://online.atol.ru/possystem/v4/getToken',
        status_code=status_code,
        json={
            'error': {
                'error_id': '4475d6d8d-844d-4d05-aa8b-e3dbdf3defd5',
                'code': 12,
                'text': 'Sorry',
                'type': 'system',
            },
            'timestamp': '30.11.2017 17:58:53',
        },
    )

    with pytest.raises(exceptions.AtolAuthError, match='Sorry'):
        auth.get_atol_token()


def test_cache(fetch):
    for _ in range(3):
        auth.get_atol_token()

    fetch.assert_called_once()
