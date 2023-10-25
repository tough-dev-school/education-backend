from dataclasses import dataclass

from rest_framework.request import Request
import stripe

from django.conf import settings

from app.services import BaseService
from orders.models import Order
from stripebank.bank import StripeBank
from stripebank.models import StripeNotification
from stripebank.services.stripe_webhook_router import stripe_router


@stripe_router.register(event_type="checkout.session.completed")
def checkout_session_completed(webhook_event: stripe.Event) -> None:
    stripe_checkout_event = webhook_event.data.object

    StripeNotification.objects.create(
        stripe_id=stripe_checkout_event["id"],
        order=Order.objects.get(slug=stripe_checkout_event["client_reference_id"]),
        event_type=webhook_event.type,
        amount=StripeBank.convert_amount(stripe_checkout_event["amount_total"]),
        payment_intent=stripe_checkout_event["payment_intent"],
        raw=webhook_event,
    )


@stripe_router.register(event_type="charge.refunded")
def charge_refunded(webhook_event: stripe.Event) -> None:
    charge_refunded_event = webhook_event.data.object

    StripeNotification.objects.create(
        stripe_id=charge_refunded_event["id"],
        order=Order.objects.get(stripe_notifications__payment_intent=charge_refunded_event["payment_intent"]),
        event_type=webhook_event.type,
        amount=StripeBank.convert_amount(charge_refunded_event["amount_refunded"]),
        payment_intent=charge_refunded_event["payment_intent"],
        raw=webhook_event,
    )


@dataclass
class StripeWebhookRouter(BaseService):
    request: Request

    def act(self) -> None:
        webhook_event = self.validate_webhook(self.request)
        handler = stripe_router.get(webhook_event.type)

        handler(webhook_event)

    def validate_webhook(self, request: Request) -> stripe.Event:
        stripe.api_key = settings.STRIPE_API_KEY

        return stripe.Webhook.construct_event(
            payload=request.body,
            sig_header=request.headers.get("STRIPE_SIGNATURE", ""),
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
