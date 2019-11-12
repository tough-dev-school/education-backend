from decimal import Decimal

import pytest

from tinkoff.exceptions import TinkoffPaymentNotificationInvalidToken
from tinkoff.models import PaymentNotification

pytestmark = [
    pytest.mark.django_db,
]


def test_success_creation(anon):
    anon.post('/api/v2/banking/tinkoff-notifications/', {
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
    }, expected_status_code=200)

    instance = PaymentNotification.objects.last()

    assert instance.terminal_key == '1321054611234DEMO'
    assert instance.order_id == 201709
    assert instance.success is True
    assert instance.status == 'AUTHORIZED'
    assert instance.payment_id == 8742591
    assert instance.error_code == '0'
    assert instance.amount == Decimal('98.55')
    assert instance.rebill_id == 101709
    assert instance.card_id == 322264
    assert instance.pan == '430000******0777'
    assert instance.data is None
    assert instance.token == 'b906d28e76c6428e37b25fcf86c0adc52c63d503013fdd632e300593d165766b'
    assert instance.exp_date == '1122'


def test_success_response(anon):
    got = anon.post('/api/v2/banking/tinkoff-notifications/', {
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
    }, expected_status_code=200)

    assert got == 'OK'


def test_creation_with_invalid_token(api):
    with pytest.raises(TinkoffPaymentNotificationInvalidToken):
        api.post('/api/v2/banking/tinkoff-notifications/', {
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
        }, expected_status_code=200)
