import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def reference_request():
    """From here: https://oplata.tinkoff.ru/landing/develop/documentation/request_sign"""
    return {
        "TerminalKey": "TinkoffBankTest",
        "Amount": "100000",
        "OrderId": "TokenExample",
        "Description": "test",
        "DATA": {
            "Phone": "+71234567890",
            "Email": "a@test.com",
        },
        "Receipt": {
            "Email": "a@test.ru",
            "Phone": "+79031234567",
            "Taxation": "osn",
            "Items": [
                {
                    "Name": "Наименование товара 1",
                    "Price": 10000,
                    "Quantity": 1.00,
                    "Amount": 10000,
                    "Tax": "vat10",
                    "Ean13": "0123456789",
                },
            ],
        },
    }


def test_signature(tinkoff, reference_request):
    assert tinkoff._get_token(reference_request) == '597C160C8C348FB14C63C820C54B712468923A74FD111AC6B0ECDA01FB5F4716'


def test_signature_without_data_and_receipt(tinkoff, reference_request):
    del reference_request['DATA']
    del reference_request['Receipt']

    assert tinkoff._get_token(reference_request) == '597C160C8C348FB14C63C820C54B712468923A74FD111AC6B0ECDA01FB5F4716'


def test_signature_with_integer_int(tinkoff, reference_request):
    reference_request['OrderId'] = 100500

    assert tinkoff._get_token(reference_request) == '2F182D493F0488BDE0750D1BDB8B1DE3A10BBE0A38358A89C8EA93972A55F453'
