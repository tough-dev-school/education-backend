from typing import Any, Type

from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from apps.banking import price_calculator
from apps.banking.base import Bank
from apps.banking.selector import get_bank_or_default
from apps.orders.api.serializers import OrderDraftRequestSerializer, Price, PriceSerializer
from apps.orders.api.throttling import OrderDraftThrottle
from apps.orders.models import Order, PromoCode
from apps.products.api.serializers import CourseSimpleSerializer
from apps.products.models import Course
from core.throttling import PublicIDThrottle
from core.views import AnonymousAPIView


@extend_schema(
    responses={
        301: None,
    }
)
class OrderConfirmationView(RetrieveAPIView):
    """Redirects user to the confirmation URL"""

    queryset = Order.objects.available_to_confirm()
    lookup_field = "slug"
    permission_classes = [AllowAny]
    throttle_classes = [PublicIDThrottle]

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirect:  # type: ignore
        order = self.get_object()

        order.set_paid()  # will be shipped on first confirmation

        return HttpResponseRedirect(redirect_to=order.item.confirmation_success_url)


class OrderDraftView(AnonymousAPIView):
    throttle_classes = [OrderDraftThrottle]

    @extend_schema(
        request=OrderDraftRequestSerializer,
        responses=[
            inline_serializer(
                name="OrderDraftSerializer",
                fields={
                    "course": CourseSimpleSerializer(),
                    "price": PriceSerializer(),
                },
            ),
        ],
        examples=[
            OpenApiExample(
                name="Product slug",
                request_only=True,
                value={
                    "course": "popug-3-self",
                },
            ),
            OpenApiExample(
                name="Promocode",
                request_only=True,
                value={
                    "course": "popug-3-self",
                    "promocode": "MYSECRETCODE",
                },
            ),
            OpenApiExample(
                name="Particular bank",
                request_only=True,
                value={
                    "course": "popug-3-self",
                    "desired_bank": "dolyame",
                },
            ),
            OpenApiExample(
                name="Default response",
                response_only=True,
                status_codes=[200],
                value={
                    "course": {
                        "name": "Коммуникации систем (самостоятельно)",
                        "name_international": "System communications (self)",
                    },
                    "price": {
                        "price": "33000",
                        "formatted_price": "33 000",
                        "currency": "RUB",
                        "currency_symbol": "₽",
                    },
                },
            ),
        ],
    )
    def post(self, request: Request) -> Response:
        """Create an order draft"""
        OrderDraftRequestSerializer(data=request.data).is_valid(raise_exception=True)

        course = self.get_course(request)
        promocode = self.get_promocode(request)
        Bank = self.get_bank(request)

        price = promocode.apply(course) if promocode is not None else course.price
        price = price_calculator.to_bank(Bank, price)

        return Response(
            status=200,
            data={
                "course": CourseSimpleSerializer(instance=course).data,
                "price": PriceSerializer(instance=Price(price, Bank)).data,
            },
        )

    @staticmethod
    def get_course(request: Request) -> Course:
        return Course.objects.get(slug=request.data["course"])

    @staticmethod
    def get_promocode(request: Request) -> PromoCode | None:
        promocode = request.data.get("promocode")
        if promocode is not None:
            return PromoCode.objects.get_or_nothing(name=promocode)

    @staticmethod
    def get_bank(request: Request) -> Type[Bank]:
        return get_bank_or_default(desired=request.data.get("desired_bank"))
