from typing import Any, TYPE_CHECKING

from drf_spectacular.utils import extend_schema
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from django.http import HttpResponseRedirect

from banking.selector import get_bank
from orders.api.base import PromocodeView
from products.api import serializers
from products.api.serializers import PurchaseSerializer
from products.models import Course
from products.services.purchase_creator import PurchaseCreator

if TYPE_CHECKING:
    from rest_framework.request import Request

    from orders.models import Order


class CourseViewSet(GenericViewSet, RetrieveModelMixin):
    lookup_field = "slug"
    serializer_class = serializers.CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]


class CoursePromocodeView(PromocodeView):
    product_model = Course


class CoursePurchaseView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(request=PurchaseSerializer, responses={301: None})
    def post(self, request: "Request", slug: str | None = None, **kwargs: dict[str, Any]) -> HttpResponseRedirect:
        item = get_object_or_404(Course, slug=slug)
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        data.pop("redirect_url", None)
        success_url = data.pop("success_url", None)

        order = PurchaseCreator(item, **data)()
        payment_link = self.get_payment_link(order, data.get("desired_bank"), success_url)

        return HttpResponseRedirect(redirect_to=payment_link)

    def get_payment_link(self, order: "Order", desired_bank: str | None, success_url: str | None) -> str:
        Bank = get_bank(desired=desired_bank)
        bank = Bank(
            order=order,
            request=self.request,
            success_url=success_url,
        )

        return bank.get_initial_payment_url()
