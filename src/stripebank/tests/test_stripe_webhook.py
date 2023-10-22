from decimal import Decimal
import json
import pytest

from stripebank.models import StripeNotification

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _disable_signature_verification(mocker):
    mocker.patch("stripe.webhook.WebhookSignature.verify_header", return_value=True)


@pytest.fixture
def webhook_checkout_completed(order):
    with open("./stripebank/tests/.fixtures/webhook_checkout_session_completed.json", "r") as fp:
        webhook = json.load(fp)
        webhook["data"]["object"]["client_reference_id"] = order.slug

        return webhook


def test(anon, webhook_checkout_completed, order):
    anon.post("/api/v2/banking/stripe-webhooks/", webhook_checkout_completed, expected_status_code=200)

    result = StripeNotification.objects.last()

    assert result.order == order
    assert result.stripe_id == "cs_test_a12qUdXreNQ0FVqOCg24WBjqWNGYRtdx9wST9jmvqcAf2ivfDE6QjC1brX"
    assert result.amount == Decimal("23333.10")
    assert result.event_type == "checkout.session.completed"
    assert result.payment_intent == "pi_3KgCCkLWSHwWFYUs1nL5b9Bj"
    assert result.raw["id"] == "evt_1KgCDfLWSHwWFYUsv8vN2HnN"
