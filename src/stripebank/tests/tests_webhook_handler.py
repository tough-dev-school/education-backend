from contextlib import nullcontext as does_not_raise
from decimal import Decimal
import pytest

import stripe

from stripebank.models import StripeNotification
from stripebank.webhook_handler import StripeWebhookHandler

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def construct_event():
    return lambda event_payload: stripe.Event.construct_from(
        values=event_payload,
        key="valid_stripe_api_key",
    )


@pytest.fixture
def handler():
    return lambda webhook_event: StripeWebhookHandler(webhook_event)()


def test_create_stripe_notification_on_checkout_session_completed(handler, webhook_checkout_session_completed, order, construct_event):
    event_checkout_session_completed = construct_event(webhook_checkout_session_completed)

    handler(event_checkout_session_completed)

    stripe_notification = StripeNotification.objects.last()
    assert stripe_notification is not None
    assert stripe_notification.order == order
    assert stripe_notification.stripe_id == "cs_test_a12qUdXreNQ0FVqOCg24WBjqWNGYRtdx9wST9jmvqcAf2ivfDE6QjC1brX"
    assert stripe_notification.amount == Decimal("23333.10")
    assert stripe_notification.event_type == "checkout.session.completed"
    assert stripe_notification.payment_intent == "pi_3KgCCkLWSHwWFYUs1nL5b9Bj"
    assert stripe_notification.raw == webhook_checkout_session_completed


@pytest.mark.usefixtures("stripe_notification_checkout_completed")
def test_create_stripe_notification_on_charge_refunded(handler, order, webhook_charge_refunded, construct_event):
    event_charge_refunded = construct_event(webhook_charge_refunded)

    handler(event_charge_refunded)

    refund_stripe_notification = StripeNotification.objects.last()
    assert refund_stripe_notification.event_type == "charge.refunded"
    assert refund_stripe_notification.order == order
    assert refund_stripe_notification.amount == Decimal("70.00")
    assert refund_stripe_notification.payment_intent == "pi_3O42fCHFzM1bXe8Q0EbUXgsQ"
    assert refund_stripe_notification.stripe_id == "ch_3O42fCHFzM1bXe8Q05ZonSIi"
    assert refund_stripe_notification.raw == webhook_charge_refunded


def test_do_nothing_on_valid_but_not_registered_webhooks(handler, load_stipe_webhook, construct_event):
    webhook_payment_intent_succeeded = load_stipe_webhook("webhook_payment_intent_succeeded.json")

    with does_not_raise():
        handler(construct_event(webhook_payment_intent_succeeded))

    assert StripeNotification.objects.count() == 0
