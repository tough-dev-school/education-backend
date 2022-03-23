import pytest
from decimal import Decimal

from stripebank.models import StripeNotification

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture(autouse=True)
def _disable_signature_verification(mocker):
    mocker.patch('stripe.webhook.WebhookSignature.verify_header', return_value=True)


def test(anon, webhook):
    anon.post('/api/v2/banking/stripe-webhooks/', webhook, expected_status_code=200)

    result = StripeNotification.objects.last()

    assert result.order_id == 'tds-5978'
    assert result.stripe_id == 'cs_test_a12qUdXreNQ0FVqOCg24WBjqWNGYRtdx9wST9jmvqcAf2ivfDE6QjC1brX'
    assert result.amount == Decimal('23333.10')
    assert result.payment_status == 'paid'
    assert result.status == 'complete'
    assert result.raw['id'] == 'evt_1KgCDfLWSHwWFYUsv8vN2HnN'
