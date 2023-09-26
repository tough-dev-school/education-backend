from typing import Any, TYPE_CHECKING

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponseRedirect

from app.pricing import format_price
from banking import price_calculator
from banking.selector import BANK_KEYS
from banking.selector import get_bank
from orders.api.serializers import PromocodeSerializer
from orders.api.throttling import PromocodeThrottle
from orders.api.throttling import PurchaseThrottle
from orders.models import PromoCode
from orders.services.purchase_creator import PurchaseCreator
from products.api.serializers import PurchaseSerializer
from products.models import Course

if TYPE_CHECKING:
    from rest_framework.request import Request


class PromocodeView(APIView):
    throttle_classes = [PromocodeThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        responses=PromocodeSerializer,
        parameters=[
            OpenApiParameter(name="promocode", type=str),
            OpenApiParameter(name="desired_bank", type=str, many=False, enum=BANK_KEYS),
        ],
    )
    def get(self, request: "Request", slug: str | None = None, **kwargs: dict[str, Any]) -> Response:
        item = get_object_or_404(Course, slug=slug)
        promocode = self._get_promocode(request)

        price = promocode.apply(item) if promocode is not None else item.price
        Bank = get_bank(desired=request.GET.get("desired_bank"))
        price = price_calculator.to_bank(Bank, price)

        serializer = PromocodeSerializer(
            {
                "price": price,
                "formatted_price": format_price(price),
                "currency": Bank.currency,
                "currency_symbol": Bank.currency_symbol,
            }
        )

        return Response(serializer.data)

    def _get_promocode(self, request: "Request") -> PromoCode | None:
        try:
            promocode_name = request.GET["promocode"]
        except KeyError:
            return None

        return PromoCode.objects.get_or_nothing(name=promocode_name)


class PurchaseView(APIView):
    throttle_classes = [PurchaseThrottle]
    permission_classes = [AllowAny]

    @extend_schema(request=PurchaseSerializer, responses={301: None})
    def post(self, request: "Request", slug: str | None = None, **kwargs: dict[str, Any]) -> HttpResponseRedirect:
        item = get_object_or_404(Course, slug=slug)
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        purchase_creator = PurchaseCreator(
            item=item,
            subscribe=data.get("subscribe"),
            user_name=data.get("name"),
            email=data.get("email"),
            promocode=data.get("promocode"),
            desired_bank=data.get("desired_bank"),
            success_url=data.get("success_url"),
            redirect_url=data.get("redirect_url"),
        )

        payment_link = purchase_creator()
        return HttpResponseRedirect(redirect_to=payment_link)
