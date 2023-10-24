from typing import Any

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings

from stripebank.services.stripe_webhook_router import StripeWebhookRouter


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]  # validation is done later by stripe StripeWebhookSaver

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        StripeWebhookRouter(
            request=request,
            stripe_webhook_secret=settings.STRIPE_WEBHOOK_SECRET,
        )()

        return Response({"success": True})
