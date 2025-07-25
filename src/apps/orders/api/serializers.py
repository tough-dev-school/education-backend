from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Type

from rest_framework import serializers

from apps.banking.base import Bank
from apps.banking.selector import BANK_CHOICES
from apps.products.models import Course
from core.pricing import format_price


@dataclass
class Price:
    price: Decimal
    bank: Type[Bank]


class PriceSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=9, decimal_places=2)
    formatted_price = serializers.CharField()
    currency = serializers.CharField()
    currency_symbol = serializers.CharField()

    def to_representation(self, instance: Price) -> dict[str, Any]:
        return {
            "price": str(instance.price).replace(".00", ""),
            "formatted_price": format_price(instance.price),
            "currency": instance.bank.currency,
            "currency_symbol": instance.bank.currency_symbol,
        }


class OrderDraftRequestSerializer(serializers.Serializer):
    course = serializers.SlugRelatedField(queryset=Course.objects.all(), slug_field="slug")
    promocode = serializers.CharField(required=False)
    desired_bank = serializers.ChoiceField(choices=BANK_CHOICES, required=False)
