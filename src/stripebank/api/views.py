from typing import Any

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe

from django.conf import settings

from app.exceptions import AppServiceException
from stripebank.webhook_handler import StripeWebhookHandler


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]  # validation is done later by 'validate_webhook' using stripe.Webhook.construct_event

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        webhook_event = self.validate_webhook(request)

        StripeWebhookHandler(webhook_event)()

        return Response({"success": True})

    def validate_webhook(self, request: Request) -> stripe.Event:
        try:
            return stripe.Webhook.construct_event(
                payload=request.body,
                sig_header=request.headers.get("STRIPE_SIGNATURE", ""),
                secret=settings.STRIPE_WEBHOOK_SECRET,
                api_key=settings.STRIPE_API_KEY,
            )

        except stripe.error.StripeError:
            raise AppServiceException("Not a valid webhook request")
