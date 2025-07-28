from typing import TYPE_CHECKING, Any

from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.banking import price_calculator
from apps.banking.selector import BANK_KEYS, get_bank_or_default
from apps.orders.api.serializers import Price, PriceSerializer
from apps.orders.api.throttling import OrderDraftThrottle, PurchaseThrottle
from apps.orders.models import PromoCode
from apps.orders.services import OrderCreator
from apps.products.api.serializers import PurchaseSerializer
from apps.products.models import Course
from apps.users.services import UserCreator

if TYPE_CHECKING:
    from rest_framework.request import Request

    from apps.orders.models import Order
    from apps.users.models import User


class PromocodeView(APIView):
    throttle_classes = [OrderDraftThrottle]
    permission_classes = [AllowAny]

    @extend_schema(
        responses=PriceSerializer,
        parameters=[
            OpenApiParameter(name="promocode", type=str),
            OpenApiParameter(name="desired_bank", type=str, many=False, enum=BANK_KEYS),
        ],
    )
    def get(self, request: "Request", slug: str | None = None, **kwargs: dict[str, Any]) -> Response:
        item = get_object_or_404(Course, slug=slug)
        promocode = self._get_promocode(request)

        price = promocode.apply(item) if promocode is not None else item.price
        Bank = get_bank_or_default(desired=request.GET.get("desired_bank"))
        price = price_calculator.to_bank(Bank, price)

        serializer = PriceSerializer(instance=Price(price, Bank))

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

    @extend_schema(request=PurchaseSerializer, responses={302: None})
    def post(self, request: "Request", slug: str | None = None, **kwargs: dict[str, Any]) -> HttpResponseRedirect:
        item = get_object_or_404(Course, slug=slug)
        serializer = PurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_or_create_user(
            name=serializer.validated_data.get("name"),
            email=serializer.validated_data.get("email"),
        )
        order = self.create_order(
            user=user,
            item=item,
            data=serializer.validated_data,
        )

        payment_link = self.get_payment_link(
            order,
            success_url=serializer.validated_data.get("success_url"),
            redirect_url=serializer.validated_data.get("redirect_url"),
        )
        return HttpResponseRedirect(redirect_to=payment_link)

    @staticmethod
    def get_or_create_user(name: str, email: str) -> "User":
        return UserCreator(
            name=name,
            email=email.strip(),
            subscribe=True,
        )()

    @staticmethod
    def create_order(user: "User", item: Course, data: dict) -> "Order":
        create_order = OrderCreator(
            user=user,
            item=item,
            promocode=data.get("promocode"),
            desired_bank=data.get("desired_bank"),
            analytics=data.get("analytics"),
        )

        return create_order()

    @staticmethod
    def get_payment_link(order: "Order", success_url: str | None, redirect_url: str | None) -> str:
        # Use course's purchase_success_url if no success_url is provided
        if success_url is None:
            success_url = order.item.purchase_success_url

        Bank = get_bank_or_default(desired=order.bank_id)
        bank = Bank(
            order=order,
            success_url=success_url,
            redirect_url=redirect_url,
        )

        return bank.get_initial_payment_url()
