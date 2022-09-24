from django.http import HttpResponseRedirect
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from app.throttling import PublicIDThrottle
from orders.models import Order


class OrderConfirmationView(RetrieveAPIView):
    queryset = Order.objects.available_to_confirm()
    lookup_field = 'slug'
    permission_classes = [AllowAny]
    throttle_classes = [PublicIDThrottle]

    def retrieve(self, request: Request, *args, **kwargs) -> HttpResponseRedirect:  # type: ignore
        order = self.get_object()

        order.set_paid()  # will be shipped on first confirmation

        return HttpResponseRedirect(redirect_to=order.item.confirmation_success_url)
