from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

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

    def act(self) -> None:
        handler = self.handlers.get(self.webhook_event.type, self.default_handler)
        handler(self.webhook_event)

    def default_handler(self, webhook_event: stripe.Event) -> None:
        pass

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
