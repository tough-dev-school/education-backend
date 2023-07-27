from abc import ABCMeta
from abc import abstractmethod
from typing import Any, Type, TYPE_CHECKING

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.pricing import format_price
from banking import price_calculator
from banking.selector import get_bank
from orders.api.serializers import PromocodeSerializer
from orders.models import PromoCode

if TYPE_CHECKING:
    from rest_framework.request import Request

    from products.models.base import Shippable


class PromocodeView(APIView, metaclass=ABCMeta):
    throttle_classes = []
    permission_classes = [AllowAny]

    @property
    @abstractmethod
    def product_model(self) -> Type["Shippable"]:
        ...

    @extend_schema(
        responses=PromocodeSerializer,
        parameters=[
            OpenApiParameter(name="promocode", type=str),
            OpenApiParameter(name="desired_bank", type=str),
        ],
    )
    def get(self, request: "Request", slug: str | None = None, **kwargs: dict[str, Any]) -> Response:
        item = get_object_or_404(self.product_model, slug=slug)
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
