from typing import Any

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import stripe

from django.conf import settings

from orders.models import Order
from stripebank.api.serializers import StripeNotificationSerializer


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]  # validation is done later by stripe library

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        payload = request.body.decode(request.encoding or "utf-8")
        stripe.api_key = settings.STRIPE_API_KEY
        sig_header = request.headers.get("STRIPE_SIGNATURE")

        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)  # type: ignore

        if event["type"] == "checkout.session.completed":
            serializer = StripeNotificationSerializer(
                data={
                    **event["data"]["object"],
                    "order": Order.objects.get(slug=event["data"]["object"]["client_reference_id"]).pk,
                    "raw": event,
                }
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({"success": True})
