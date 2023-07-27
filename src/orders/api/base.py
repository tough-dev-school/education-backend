from abc import ABCMeta
from abc import abstractmethod
from typing import Any, Type, TYPE_CHECKING

from drf_spectacular.utils import extend_schema
from drf_spectacular.utils import OpenApiParameter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import HttpResponseRedirect

from app.pricing import format_price
from banking import price_calculator
from banking.selector import get_bank
from orders.api.serializers import PromocodeSerializer
from orders.api.serializers import PurchaseSerializer
from orders.models import Order
from orders.models import PromoCode
from orders.services.order_creator import OrderCreator
from users.models import User
from users.services import UserCreator

if TYPE_CHECKING:
    from products.models.base import Shippable


class PromocodeView(APIView, metaclass=ABCMeta):
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
    def get(self, request: Request, slug: str | None = None, **kwargs: dict[str, Any]) -> Response:
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

    def _get_promocode(self, request: Request) -> PromoCode | None:
        try:
            promocode_name = request.GET["promocode"]
        except KeyError:
            return None

        return PromoCode.objects.get_or_nothing(name=promocode_name)


class PurchaseView(APIView, metaclass=ABCMeta):
    permission_classes = [AllowAny]

    @property
    @abstractmethod
    def product_model(self) -> Type["Shippable"]:
        ...

    @extend_schema(request=PurchaseSerializer, responses={301: None})
    def post(self, request: Request, slug: str | None = None, **kwargs: dict[str, Any]) -> HttpResponseRedirect:
        item = get_object_or_404(self.product_model, slug=slug)
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        order = self._create_order(data=data, item=item)
        payment_link = self.get_payment_link(order, data=data)

        return HttpResponseRedirect(redirect_to=payment_link)

    @property
    def subscribe(self) -> bool:
        return str(self.request.POST.get("subscribe", False)).lower() in [
            "true",
            "1",
            "yes",
        ]

    def _create_order(self, data: dict, item: "Shippable") -> Order:
        creator = OrderCreator(
            user=self._create_user(
                name=data["name"],
                email=data["email"],
                subscribe=self.subscribe,
            ),
            item=item,
            promocode=data.get("promocode"),
            desired_bank=data.get("desired_bank"),
        )
        return creator()

    def _create_user(self, name: str, email: str, subscribe: bool = False) -> User:
        return UserCreator(
            name=name,
            email=email.strip(),
            subscribe=subscribe,
        )()

    def get_payment_link(self, order: Order, data: dict) -> str:
        Bank = get_bank(desired=data.get("desired_bank"))
        bank = Bank(
            order=order,
            request=self.request,
            success_url=data.get("success_url"),
        )

        return bank.get_initial_payment_url()
