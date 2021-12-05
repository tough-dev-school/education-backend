from django.http import HttpResponse
from rest_framework.views import APIView

from tinkoff.api.permissions import TinkoffCreditNetmaskPermission
from tinkoff.api.serializers import CreditNotificationSerializer, PaymentNotificationSerializer


class TinkoffPaymentNotificationsView(APIView):
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
