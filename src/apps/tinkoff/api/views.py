from typing import Any

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from django.http import HttpResponse

from apps.orders.models import Order
from apps.tinkoff.api.permissions import DolyameNetmaskPermission
from apps.tinkoff.api.serializers import DolyameNotificationSerializer
from apps.tinkoff.api.serializers import PaymentNotificationSerializer
from apps.tinkoff.token_validator import TinkoffNotificationsTokenValidator


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


class DolyameNotificationsView(APIView):
    """Receive dolyame notifications."""

    permission_classes = [DolyameNetmaskPermission]

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
