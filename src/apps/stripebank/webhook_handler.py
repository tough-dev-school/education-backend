from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

import sentry_sdk
import stripe

from apps.orders.models import Order
from apps.stripebank.bank import StripeBank
from apps.stripebank.models import StripeNotification
from core.services import BaseService


@dataclass
class StripeWebhookHandler(BaseService):
    webhook_event: stripe.Event

    @property
    def handlers(self) -> dict[str, Callable]:
        return {
            "checkout.session.completed": self.checkout_session_completed,
            "charge.refunded": self.charge_refunded,
        }

    @property
    def safe_low_interested_event_types(self) -> set[str]:
        """Safe low interested notifications that don't require their own handler.
        These events are saved without being linked to an order and no sentry notification is sent.
        """
        return {
            "payment_intent.succeeded",
        }

    def act(self) -> None:
        handler = self.handlers.get(self.webhook_event.type, self.default_handler)
        handler(self.webhook_event)

    def default_handler(self, webhook_event: stripe.Event) -> None:
        StripeNotification.objects.create(
            stripe_id=webhook_event.data.object["id"],
            event_type=webhook_event.type,
            raw=webhook_event,
        )

        if webhook_event.type not in self.safe_low_interested_event_types:
            sentry_sdk.capture_message(f"Suspicious Stripe event received: {webhook_event.type}")

    def checkout_session_completed(self, webhook_event: stripe.Event) -> None:
        stripe_checkout_event = webhook_event.data.object

        StripeNotification.objects.create(
            stripe_id=stripe_checkout_event["id"],
            order=Order.objects.get(slug=stripe_checkout_event["client_reference_id"]),
            event_type=webhook_event.type,
            amount=self.convert_amount(stripe_checkout_event["amount_total"]),
            payment_intent=stripe_checkout_event["payment_intent"],
            raw=webhook_event,
        )

    def charge_refunded(self, webhook_event: stripe.Event) -> None:
        charge_refunded_event = webhook_event.data.object

        StripeNotification.objects.create(
            stripe_id=charge_refunded_event["id"],
            order=Order.objects.get(stripe_notifications__payment_intent=charge_refunded_event["payment_intent"]),
            event_type=webhook_event.type,
            amount=self.convert_amount(charge_refunded_event["amount_refunded"]),
            payment_intent=charge_refunded_event["payment_intent"],
            raw=webhook_event,
        )

    @staticmethod
    def convert_amount(stripe_amount: int) -> Decimal:
        return Decimal(Decimal(stripe_amount) / 100 * StripeBank.ue)
