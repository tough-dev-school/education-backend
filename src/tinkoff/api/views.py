import uuid
from django.http import HttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from tinkoff import tasks
from tinkoff.api.permissions import DolyameNetmaskPermission, TinkoffCreditNetmaskPermission
from tinkoff.api.serializers import (
    CreditNotificationSerializer, DolyameNotificationSerializer, PaymentNotificationSerializer)


class TinkoffPaymentNotificationsView(APIView):
    permission_classes = [AllowAny]  # validation is done later via supplied JSON

    def post(self, request, *args, **kwargs):
        serializer = PaymentNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse('OK')


class TinkoffCreditNotificationsView(APIView):
    permission_classes = [TinkoffCreditNetmaskPermission]

    def post(self, request, *args, **kwargs):
        serializer = CreditNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse('OK')


class DolyameNotificationsView(APIView):
    """Receive dolyame notifications, automatically commiting back
    ones that are waiting for commit
    """
    permission_classes = [DolyameNetmaskPermission]

    def post(self, request, *args, **kwargs):
        serializer = DolyameNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification = serializer.save()

        if notification.status == 'wait_for_commit':
            tasks.commit_dolyame_order.apply_async(
                countdown=10,
                kwargs={
                    'order_id': notification.order_id.replace('tds-', ''),
                    'idempotency_key': str(uuid.uuid4()),
                },
            )

        return HttpResponse('OK')
