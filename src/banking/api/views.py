from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django.http import HttpResponse

from banking.models import Receipt
from orders.models import Order


class AtolWebhookView(APIView):
    permission_classes = [AllowAny]  # validation is done later via supplied JSON

    def get(self, request, *args, **kwargs):
        return HttpResponse("Temporary answering you OK to check what atol wants sending GET here instead of POST")

    def post(self, request, *args, **kwargs):
        Receipt.objects.create(
            provider="atol",
            source_ip=request.META["REMOTE_ADDR"],
            data=request.data,
            order_id=Order.objects.get(slug=request.data["external_id"]).pk,
        )

        return HttpResponse("ok")
