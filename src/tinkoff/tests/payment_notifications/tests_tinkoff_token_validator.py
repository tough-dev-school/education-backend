import pytest

from tinkoff.exceptions import TinkoffPaymentNotificationInvalidToken, TinkoffPaymentNotificationNoTokenPassed
from tinkoff.token_validator import TinkoffNotificationsTokenValidator


@pytest.mark.parametrize('data', [
    {
        'TerminalKey': '1321054611234DEMO',
        'OrderId': 201709,
        'Success': True,
        'Status': 'AUTHORIZED',
        'PaymentId': 8742591,
        'ErrorCode': 0,
        'Amount': 9855,
        'RebillId': 101709,
        'CardId': 322264,
        'Pan': '430000******0777',
        'Token': 'b906d28e76c6428e37b25fcf86c0adc52c63d503013fdd632e300593d165766b',
        'ExpDate': '1122',
    },
])
def test_success_validation(data):
    validator = TinkoffNotificationsTokenValidator(data)

    assert validator() is True


@pytest.mark.parametrize('data', [
    {
        'TerminalKey': '1321054611234DEMO',
        'OrderId': 201709,
        'Success': True,
        'Status': 'AUTHORIZED',
        'PaymentId': 8742591,
        'ErrorCode': 0,
        'Amount': 9855,
        'RebillId': 101709,
        'CardId': 322264,
        'Pan': '430000******0777',
        'ExpDate': '1122',
    },
])
def test_no_token_passed_for_validation(data):
    validator = TinkoffNotificationsTokenValidator(data)

    with pytest.raises(TinkoffPaymentNotificationNoTokenPassed) as excinfo:
        validator()
    assert data in excinfo.value.args


@pytest.mark.parametrize('data', [
    {
        'TerminalKey': 'Terminal Key',
        'OrderId': 123,
        'Success': True,
        'Status': 'CONFIRMED',
        'PaymentId': 12345,
        'Amount': 100.50,
        'RebillId': 67890,
        'CardId': 123456789,
        'Pan': '1234**********56',
        'DATA': 'some random stuff',
        'Token': 'token',
        'ExpDate': '0118',
    },
])
def test_failed_validation(data):
    validator = TinkoffNotificationsTokenValidator(data)

    with pytest.raises(TinkoffPaymentNotificationInvalidToken) as excinfo:
        validator()
    assert data in excinfo.value.args
