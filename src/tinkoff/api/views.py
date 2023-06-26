from typing import Any
import uuid

from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.views import APIView

from django.http import HttpResponse

from orders.models import Order
from tinkoff import tasks
from tinkoff.api.permissions import DolyameNetmaskPermission
from tinkoff.api.permissions import TinkoffCreditNetmaskPermission
from tinkoff.api.serializers import CreditNotificationSerializer
from tinkoff.api.serializers import DolyameNotificationSerializer
from tinkoff.api.serializers import PaymentNotificationSerializer
from tinkoff.token_validator import TinkoffNotificationsTokenValidator


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


class TinkoffCreditNotificationsView(APIView):
    permission_classes = [TinkoffCreditNetmaskPermission]

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        serializer = CreditNotificationSerializer(
            data={
                "id": Order.objects.get(slug=request.data.pop("id")).pk,
                **request.data,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse("OK")


class DolyameNotificationsView(APIView):
    """Receive dolyame notifications, automatically commiting back
    ones that are waiting for commit
    """

    permission_classes = [DolyameNetmaskPermission]

    def post(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> HttpResponse:
        serializer = DolyameNotificationSerializer(
            data={
                "order": Order.objects.get(slug=request.data.pop("id")).pk,
                **request.data,
            }
        )
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        if notification.status == "wait_for_commit":
            tasks.commit_dolyame_order.apply_async(
                countdown=10,
                kwargs={
                    "order_id": notification.order.pk,
                    "idempotency_key": str(uuid.uuid4()),
                },
            )

        return HttpResponse("OK")
