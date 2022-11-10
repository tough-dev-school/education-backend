import pytest
from functools import partial

from tinkoff.business_client import TinkoffBusinessClient


@pytest.fixture
def client():
    return TinkoffBusinessClient()


@pytest.fixture
def bank_accounts_json():
    return [
        {
            'accountNumber': '40802678901234567890',
            'currency': '643',
            'balance': {
                'otb': 45089,
                'authorized': 0,
                'pendingPayments': 0,
                'pendingRequisitions': 0,
            },
        },
        {
            'accountNumber': '100500',
            'currency': '643',
            'balance': {
                'otb': 45089,
                'authorized': 20,
                'pendingPayments': 10,
                'pendingRequisitions': 0,
            },
        },
    ]


@pytest.fixture
def mock_tinkoff_response(httpx_mock):
    return partial(httpx_mock.add_response, url='https://business.tinkoff.ru/openapi/api/v1/bank-accounts')


@pytest.fixture
def mock_http_get(mocker):
    return mocker.patch('tinkoff.business_client.http.TinkoffBusinessHTTP.get')


def test_http_get_method_used(client, mock_http_get):
    client.get_bank_account_numbers()

    mock_http_get.assert_called_once_with('bank-accounts')


def test_returns_bank_account_numbers_only(client, mock_tinkoff_response, bank_accounts_json):
    mock_tinkoff_response(json=bank_accounts_json)

    got = client.get_bank_account_numbers()

    assert len(got) == 2
    assert '40802678901234567890' in got
    assert '100500' in got
