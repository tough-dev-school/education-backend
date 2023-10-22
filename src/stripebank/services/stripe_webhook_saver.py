from dataclasses import dataclass
from decimal import Decimal
from typing import Any, TypedDict

from rest_framework.request import Request
import stripe

from django.conf import settings

from app.services import BaseService
from orders.models import Order
from stripebank.bank import StripeBank
from stripebank.models import StripeNotification


class WebhookEvent(TypedDict):
    type: str
    data: dict[str, Any]


@dataclass
class StripeWebhookSaver(BaseService):
    request: Request
    stripe_webhook_secret: str

    def act(self) -> None:
        webhook_event = self.validate_webhook_and_get_event(self.request)
        webhook_event_type = webhook_event["type"]

        if webhook_event_type == "checkout.session.completed":
            self.save_checkout_session_completed(webhook_event)

        if webhook_event_type == "charge.refunded":
            self.save_charge_refunded(webhook_event)

    def validate_webhook_and_get_event(self, request: Request) -> WebhookEvent:
        stripe.api_key = settings.STRIPE_API_KEY
        sig_header = request.headers.get("STRIPE_SIGNATURE")

        return stripe.Webhook.construct_event(request.body, sig_header, self.stripe_webhook_secret)  # type: ignore

    def save_checkout_session_completed(self, webhook_event: WebhookEvent) -> None:
        stripe_checkout_event = webhook_event["data"]["object"]

        StripeNotification.objects.create(
            stripe_id=stripe_checkout_event["id"],
            order=Order.objects.get(slug=stripe_checkout_event["client_reference_id"]),
            event_type=webhook_event["type"],
            amount=self.convert_amount(stripe_checkout_event["amount_total"]),
            payment_intent=stripe_checkout_event["payment_intent"],
            raw=webhook_event,
        )

    def save_charge_refunded(self, webhook_event: WebhookEvent) -> None:
        charge_refunded_event = webhook_event["data"]["object"]

        StripeNotification.objects.create(
            stripe_id=charge_refunded_event["id"],
            order=Order.objects.get(stripe_notifications__payment_intent=charge_refunded_event["payment_intent"]),
            event_type=webhook_event["type"],
            amount=self.convert_amount(charge_refunded_event["amount_refunded"]),
            payment_intent=charge_refunded_event["payment_intent"],
            raw=webhook_event,
        )

    def convert_amount(self, stripe_amount: int) -> Decimal:
        return Decimal(stripe_amount / 100 * StripeBank.ue)
