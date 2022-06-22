import json
import pytest
from datetime import datetime

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def webhook(order):
    with open('./stripebank/tests/.fixtures/webhook.json', 'r') as fp:
        bank_data = json.load(fp)
        bank_data['data']['object']['client_reference_id'] = order.slug

        return bank_data


@pytest.fixture(autouse=True)
def _disable_signature_verification(mocker):
    mocker.patch('stripe.webhook.WebhookSignature.verify_header', return_value=True)


def test(anon, webhook, order):
    anon.post('/api/v2/banking/stripe-webhooks/', webhook, expected_status_code=200)

    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30)


@pytest.mark.parametrize('status', ['not-complete', 'f4ke'])
def test_wrong_status(anon, order, webhook, status):
    webhook['data']['object']['status'] = status

    anon.post('/api/v2/banking/stripe-webhooks/', webhook, expected_status_code=200)

    order.refresh_from_db()
    assert order.paid is None
