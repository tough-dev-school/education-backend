from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.banking import price_calculator
from apps.banking.api.serializers import Price, PriceSerializer
from apps.banking.selector import BANK_CHOICES
from apps.products.models import Course


class CourseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "name",
            "name_international",
            "product_name",
            "tariff_name",
        ]


class CourseWithPriceSerializer(serializers.ModelSerializer):
    """Course with commercial data. Requires bank context"""

    price = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "slug",
            "name",
            "name_international",
            "product_name",
            "tariff_name",
            "price",
        ]

    @extend_schema_field(PriceSerializer)
    def get_price(self, course: Course) -> dict:
        Bank = self.context["Bank"]  # needs to know a bank name to calculate the price
        price = price_calculator.to_bank(Bank, course.price)

        return PriceSerializer(instance=Price(price, Bank)).data


class PurchaseSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    desired_bank = serializers.ChoiceField(choices=BANK_CHOICES, required=False)
    promocode = serializers.CharField(max_length=100, required=False)
    success_url = serializers.CharField(max_length=256, required=False)
    redirect_url = serializers.CharField(max_length=256, required=False)
    subscribe = serializers.CharField(max_length=5, default="")
    analytics = serializers.CharField(required=False)

    def validate_subscribe(self, value: str | None) -> bool:
        if value:
            return value.lower() in ["true", "1", "yes"]
        return False
