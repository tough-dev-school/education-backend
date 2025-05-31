from typing import Any

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.tinkoff.api.serializers import DolyameNotificationSerializer, PaymentNotificationSerializer
from apps.tinkoff.token_validator import TinkoffNotificationsTokenValidator


@extend_schema(exclude=True)
class TinkoffPaymentNotificationsView(APIView):
    permission_classes = [AllowAny]  # validation is done later via supplied JSON

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        TinkoffNotificationsTokenValidator(payload=request.data)()

        serializer = PaymentNotificationSerializer(
            data={
                "OrderId": Order.objects.get(slug=request.data.pop("OrderId")).pk,
                **request.data,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse("OK")


@extend_schema(exclude=True)
class DolyameNotificationsView(APIView):
    """Receive dolyame notifications."""

    permission_classes = [AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        serializer = DolyameNotificationSerializer(
            data={
                "order": Order.objects.get(slug=request.data.pop("id")).pk,
                **request.data,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse("OK")
