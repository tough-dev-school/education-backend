from rest_framework import serializers

from banking.selector import BANK_CHOICES
from products.models import Course


class ShippableSerializer(serializers.ModelSerializer):
    price = serializers.CharField(source="get_price_display")
    old_price = serializers.CharField(source="get_old_price_display")
    formatted_price = serializers.CharField(source="get_formatted_price_display")

    class Meta:
        fields = [
            "slug",
            "name",
            "price",
            "old_price",
            "formatted_price",
        ]


class CourseSerializer(ShippableSerializer):
    class Meta(ShippableSerializer.Meta):
        model = Course


class CourseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "name",
        ]


class PurchaseSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    desired_bank = serializers.ChoiceField(choices=BANK_CHOICES, required=False)
    promocode = serializers.CharField(max_length=100, required=False)
    success_url = serializers.CharField(max_length=256, required=False)
    redirect_url = serializers.CharField(max_length=256, required=False)
    subscribe = serializers.CharField(max_length=5, required=False)
