from rest_framework import serializers

from apps.banking.selector import BANK_CHOICES
from apps.products.models import Course


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
    subscribe = serializers.CharField(max_length=5, default="")
    analytics = serializers.JSONField(required=False)

    def validate_subscribe(self, value: str | None) -> bool:
        if value:
            return value.lower() in ["true", "1", "yes"]
        return False
