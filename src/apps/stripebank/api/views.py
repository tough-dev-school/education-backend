from typing import Any, Type

import stripe
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.stripebank.bank import BaseStripeBank, StripeBankKZT, StripeBankUSD
from apps.stripebank.webhook_handler import StripeWebhookHandler
from core.exceptions import AppServiceException


class BaseStripeWebhookView(APIView):
    permission_classes = [AllowAny]  # validation is done later by 'validate_webhook' using stripe.Webhook.construct_event

    @property
    def bank(self) -> Type[BaseStripeBank]:
        raise NotImplementedError()

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        webhook_event = self.validate_webhook(request)

        StripeWebhookHandler(webhook_event, self.bank)()

        return Response({"success": True})

    def validate_webhook(self, request: Request) -> stripe.Event:
        try:
            return stripe.Webhook.construct_event(
                payload=request.body,
                sig_header=request.headers.get("STRIPE_SIGNATURE", ""),
                secret=self.bank.webhook_secret,
                api_key=self.bank.api_key,
            )

        except stripe.error.StripeError:
            raise AppServiceException("Not a valid webhook request")


class StripeWebhookUSDView(BaseStripeWebhookView):
    @property
    def bank(self) -> Type[BaseStripeBank]:
        return StripeBankUSD


class StripeWebhookKZTView(BaseStripeWebhookView):
    @property
    def bank(self) -> Type[BaseStripeBank]:
        return StripeBankKZT
