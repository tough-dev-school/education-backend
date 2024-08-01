from decimal import Decimal

import pytest
import stripe

from apps.stripebank.models import StripeNotification
from apps.stripebank.webhook_handler import StripeWebhookHandler

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_capture_message(mocker):
    return mocker.patch("sentry_sdk.capture_message")


@pytest.fixture
def construct_event():
    return lambda event_payload: stripe.Event.construct_from(
        values=event_payload,
        key="valid_stripe_api_key",
    )


@pytest.fixture
def webhook_payment_intent_succeeded(load_stipe_webhook):
    return load_stipe_webhook("webhook_payment_intent_succeeded.json")


@pytest.fixture
def remove_all_safe_low_interested_event_type(mocker):
    return mocker.patch(
        "apps.stripebank.webhook_handler.StripeWebhookHandler.safe_low_interested_event_types",
        new_callable=mocker.PropertyMock,
        return_value=set(),
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


def test_create_notification_for_safe_low_interested_events(handler, webhook_payment_intent_succeeded, construct_event, mock_capture_message):
    event_payment_succeeded = construct_event(webhook_payment_intent_succeeded)

    handler(event_payment_succeeded)

    mock_capture_message.assert_not_called()
    last_notification = StripeNotification.objects.last()
    assert last_notification.event_type == "payment_intent.succeeded"
    assert last_notification.order is None
    assert last_notification.amount == Decimal("0.0")
    assert last_notification.payment_intent == ""
    assert last_notification.stripe_id == "pi_3O4u2GHFzM1bXe8Q0Yiqnlpp"
    assert last_notification.raw == webhook_payment_intent_succeeded


@pytest.mark.usefixtures("remove_all_safe_low_interested_event_type")
def test_create_notification_and_alert_fow_unknown_events(handler, webhook_payment_intent_succeeded, construct_event, mock_capture_message):
    event_payment_succeeded = construct_event(webhook_payment_intent_succeeded)

    handler(event_payment_succeeded)

    mock_capture_message.assert_called_once_with("Suspicious Stripe event received: payment_intent.succeeded")
    last_notification = StripeNotification.objects.last()
    assert last_notification.event_type == "payment_intent.succeeded"
    assert last_notification.order is None
    assert last_notification.amount == Decimal("0.0")
    assert last_notification.payment_intent == ""
    assert last_notification.stripe_id == "pi_3O4u2GHFzM1bXe8Q0Yiqnlpp"
    assert last_notification.raw == webhook_payment_intent_succeeded
