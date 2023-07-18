from typing import Any

from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from django.http import HttpResponseRedirect

from app.pricing import format_price
from banking import price_calculator
from banking.selector import get_bank
from orders.api.validators import PurchaseValidator
from orders.models import Order
from orders.models import PromoCode
from orders.services.order_creator import OrderCreator
from products.models.base import Shippable
from users.models import User
from users.services import UserCreator


class PurchaseViewSet(ReadOnlyModelViewSet):
    """Abstract viewset for purchasable items"""

    @property
    def item(self) -> Shippable:
        return self.get_object()

    @property
    def subscribe(self) -> bool:
        return str(self.request.POST.get("subscribe", False)).lower() in [
            "true",
            "1",
            "yes",
        ]

    @action(methods=["POST"], detail=True)
    def purchase(self, request: Request, pk: str | None = None, **kwargs: dict[str, Any]) -> HttpResponseRedirect:
        """Direct order purchase"""
        data = request.POST

        PurchaseValidator.do(data, context={"request": self.request})

        order = self._create_order(data=data)
        payment_link = self.get_payment_link(order, data=data)

        return HttpResponseRedirect(redirect_to=payment_link)

    @action(methods=["GET"], detail=True)
    def promocode(self, request: Request, pk: str | None = None, **kwargs: dict[str, Any]) -> Response:
        promocode = self._get_promocode(request)

        price = promocode.apply(self.item) if promocode is not None else self.item.price

        Bank = get_bank(desired=request.GET.get("desired_bank"))

        price = price_calculator.to_bank(Bank, price)

        return Response(
            {
                "price": price,
                "formatted_price": format_price(price),
                "currency": Bank.currency,
                "currency_symbol": Bank.currency_symbol,
            }
        )

    def _create_order(self, data: dict) -> Order:
        creator = OrderCreator(
            user=self._create_user(
                name=data["name"],
                email=data["email"],
                subscribe=self.subscribe,
            ),
            item=self.item,
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

    def _get_promocode(self, request: Request) -> PromoCode | None:
        try:
            promocode_name = request.GET["promocode"]
        except KeyError:
            return None

        return PromoCode.objects.get_or_nothing(name=promocode_name)

    def get_payment_link(self, order: Order, data: dict) -> str:
        Bank = get_bank(desired=data.get("desired_bank"))
        bank = Bank(
            order=order,
            request=self.request,
            success_url=data.get("success_url"),
        )

        return bank.get_initial_payment_url()

    def list(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Any:
        raise MethodNotAllowed("list")
