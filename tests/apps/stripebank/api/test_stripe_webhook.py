import pytest
import stripe

from apps.stripebank.models import StripeNotification
from apps.stripebank.webhook_handler import StripeWebhookHandler

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_disable_signature_verification"),
]


@pytest.fixture
def spy_stripe_webhook_handler(mocker):
    return mocker.spy(StripeWebhookHandler, "__call__")


def test_checkout_session_completed(anon, webhook_checkout_session_completed, order, spy_stripe_webhook_handler):
    anon.post("/api/v2/banking/stripe-webhooks/", webhook_checkout_session_completed, expected_status_code=200)

    stripe_notification = StripeNotification.objects.last()
    assert stripe_notification.event_type == "checkout.session.completed"
    assert stripe_notification.order == order
    spy_stripe_webhook_handler.assert_called_once()


@pytest.mark.usefixtures("stripe_notification_checkout_completed")
def test_charge_refunded(anon, webhook_charge_refunded, order, spy_stripe_webhook_handler):
    anon.post("/api/v2/banking/stripe-webhooks/", webhook_charge_refunded, expected_status_code=200)

    stripe_notification = StripeNotification.objects.last()
    assert stripe_notification.event_type == "charge.refunded"
    assert stripe_notification.order == order
    spy_stripe_webhook_handler.assert_called_once()


def test_raise_if_signature_not_valid(anon, webhook_checkout_session_completed, mocker, spy_stripe_webhook_handler):
    mocker.patch(
        "stripe.webhook.WebhookSignature.verify_header",
        side_effect=stripe.error.SignatureVerificationError("invalid signature", sig_header="not-valid-signature"),
    )

    anon.post("/api/v2/banking/stripe-webhooks/", webhook_checkout_session_completed, expected_status_code=400)

    spy_stripe_webhook_handler.assert_not_called()
