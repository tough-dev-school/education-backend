import pytest

from apps.tinkoff.exceptions import TinkoffPaymentNotificationInvalidToken, TinkoffPaymentNotificationNoTokenPassed
from apps.tinkoff.token_validator import TinkoffNotificationsTokenValidator


@pytest.mark.parametrize(
    "payload",
    [
        {
            "TerminalKey": "1321054611234DEMO",
            "OrderId": 201709,
            "Success": True,
            "Status": "AUTHORIZED",
            "PaymentId": 8742591,
            "ErrorCode": 0,
            "Amount": 9855,
            "RebillId": 101709,
            "CardId": 322264,
            "Pan": "430000******0777",
            "Token": "b906d28e76c6428e37b25fcf86c0adc52c63d503013fdd632e300593d165766b",
            "Data": {
                "test": "__dummy",
            },
            "ExpDate": "1122",
        },
    ],
)
def test_success_validation(payload):
    validator = TinkoffNotificationsTokenValidator(payload)

    assert validator() is True


@pytest.mark.parametrize(
    "payload",
    [
        {
            "TerminalKey": "1321054611234DEMO",
            "OrderId": 201709,
            "Success": True,
            "Status": "AUTHORIZED",
            "PaymentId": 8742591,
            "ErrorCode": 0,
            "Amount": 9855,
            "RebillId": 101709,
            "CardId": 322264,
            "Pan": "430000******0777",
            "ExpDate": "1122",
        },
    ],
)
def test_no_token_passed_for_validation(payload):
    validator = TinkoffNotificationsTokenValidator(payload)

    with pytest.raises(TinkoffPaymentNotificationNoTokenPassed) as excinfo:
        validator()
    assert payload in excinfo.value.args


@pytest.mark.parametrize(
    "payload",
    [
        {
            "TerminalKey": "Terminal Key",
            "OrderId": 123,
            "Success": True,
            "Status": "CONFIRMED",
            "PaymentId": 12345,
            "Amount": 100.50,
            "RebillId": 67890,
            "CardId": 123456789,
            "Pan": "1234**********56",
            "DATA": "some random stuff",
            "Token": "token",
            "ExpDate": "0118",
        },
    ],
)
def test_failed_validation(payload):
    validator = TinkoffNotificationsTokenValidator(payload)

    with pytest.raises(TinkoffPaymentNotificationInvalidToken) as excinfo:
        validator()
    assert payload in excinfo.value.args
