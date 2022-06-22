import pytest

from banking.models import Receipt

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


def test(api, order):
    api.post('/api/v2/banking/atol-webhooks-SECRET-SALT/', {
        'uuid': '100500',
        'error': None,
        'payload': {
            'total': 22000.0,
        },
        'external_id': order.slug,
    }, expected_status_code=200)

    result = Receipt.objects.order_by('-id').first()

    assert result.order == order
    assert result.source_ip == '127.0.0.1'
    assert result.data['payload']['total'] == 22000
