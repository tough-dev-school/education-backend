from rest_framework import serializers

from products.models import Bundle
from products.models import Course
from products.models import Record


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


class RecordSerializer(ShippableSerializer):
    class Meta(ShippableSerializer.Meta):
        model = Record


class BundleSerializer(ShippableSerializer):
    class Meta(ShippableSerializer.Meta):
        model = Bundle


class PurchaseSerializer(serializers.Serializer):
    """Simple serializer used to validate purchases"""

    class Meta:
        fields = [
            "name",
            "email",
        ]

    @classmethod
    def _validate(cls, input: dict):
        instance = cls(data=input)
        instance.is_valid(raise_exception=True)


class CourseSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "name",
        ]
