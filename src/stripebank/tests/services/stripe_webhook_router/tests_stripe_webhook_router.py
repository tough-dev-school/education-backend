from contextlib import nullcontext as does_not_raise
from decimal import Decimal
import pytest

from rest_framework.test import APIRequestFactory
import stripe

from stripebank.models import StripeNotification
from stripebank.services.stripe_webhook_router import StripeWebhookRouter

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_disable_signature_verification"),
]


@pytest.fixture
def request_factory():
    factory = APIRequestFactory()

    def get_stripe_webhook_request(data: dict):
        return factory.post(
            path="/valid-webhook-url/",
            headers={
                "STRIPE_SIGNATURE": "valid-signature",
            },
            data=data,
            format="json",
        )

    return get_stripe_webhook_request


@pytest.fixture
def request_checkout_session_completed(request_factory, webhook_checkout_session_completed):
    return request_factory(webhook_checkout_session_completed)


@pytest.fixture
def request_charge_refunded(request_factory, webhook_charge_refunded):
    return request_factory(webhook_charge_refunded)


@pytest.fixture
def router():
    return lambda request: StripeWebhookRouter(request)()


def test_create_stripe_notification_on_checkout_session_completed(router, request_checkout_session_completed, order, webhook_checkout_session_completed):
    router(request_checkout_session_completed)

    stripe_notification = StripeNotification.objects.last()
    assert stripe_notification is not None
    assert stripe_notification.order == order
    assert stripe_notification.stripe_id == "cs_test_a12qUdXreNQ0FVqOCg24WBjqWNGYRtdx9wST9jmvqcAf2ivfDE6QjC1brX"
    assert stripe_notification.amount == Decimal("23333.10")
    assert stripe_notification.event_type == "checkout.session.completed"
    assert stripe_notification.payment_intent == "pi_3KgCCkLWSHwWFYUs1nL5b9Bj"
    assert stripe_notification.raw == webhook_checkout_session_completed


@pytest.mark.usefixtures("stripe_notification_checkout_completed")
def test_create_stripe_notification_on_charge_refunded(router, order, request_charge_refunded, webhook_charge_refunded):
    router(request_charge_refunded)

    refund_stripe_notification = StripeNotification.objects.last()
    assert refund_stripe_notification.event_type == "charge.refunded"
    assert refund_stripe_notification.order == order
    assert refund_stripe_notification.amount == Decimal("70.00")
    assert refund_stripe_notification.payment_intent == "pi_3O42fCHFzM1bXe8Q0EbUXgsQ"
    assert refund_stripe_notification.stripe_id == "ch_3O42fCHFzM1bXe8Q05ZonSIi"
    assert refund_stripe_notification.raw == webhook_charge_refunded


def test_do_nothing_on_valid_but_not_registered_webhooks(router, request_factory, load_stipe_webhook):
    webhook_payment_intent_succeeded = load_stipe_webhook("webhook_payment_intent_succeeded.json")

    with does_not_raise():
        router(request_factory(webhook_payment_intent_succeeded))

    assert StripeNotification.objects.count() == 0


def test_raise_if_signature_not_valid(router, request_checkout_session_completed, mocker):
    mocker.patch(
        "stripe.webhook.WebhookSignature.verify_header",
        side_effect=stripe.error.SignatureVerificationError("invalid signature", sig_header="not-valid-signature"),
    )

    with pytest.raises(stripe.error.SignatureVerificationError):
        router(request_checkout_session_completed)
