from django.http import HttpResponse
from rest_framework_tracking.mixins import LoggingMixin

from app.views import AnonymousAPIView
from tinkoff.api.serializers import PaymentNotificationSerializer


class TinkoffPaymentNotificationsView(LoggingMixin, AnonymousAPIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return HttpResponse('OK')
