import pytest

from stripebank.models import StripeNotification
from stripebank.services.stripe_webhook_router import StripeWebhookRouter

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_disable_signature_verification"),
]


@pytest.fixture
def spy_stripe_router(mocker):
    return mocker.spy(StripeWebhookRouter, "__call__")


def test_checkout_session_completed(anon, webhook_checkout_session_completed, order, spy_stripe_router):
    anon.post("/api/v2/banking/stripe-webhooks/", webhook_checkout_session_completed, expected_status_code=200)

    stripe_notification = StripeNotification.objects.last()
    assert stripe_notification.event_type == "checkout.session.completed"
    assert stripe_notification.order == order
    spy_stripe_router.assert_called_once()


@pytest.mark.usefixtures("stripe_notification_checkout_completed")
def test_charge_refunded(anon, webhook_charge_refunded, order, spy_stripe_router):
    anon.post("/api/v2/banking/stripe-webhooks/", webhook_charge_refunded, expected_status_code=200)

    stripe_notification = StripeNotification.objects.last()
    assert stripe_notification.event_type == "charge.refunded"
    assert stripe_notification.order == order
    spy_stripe_router.assert_called_once()
