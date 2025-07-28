from rest_framework import serializers

from apps.banking.selector import BANK_CHOICES
from apps.products.models import Course


class OrderDraftRequestSerializer(serializers.Serializer):
    course = serializers.SlugRelatedField(queryset=Course.objects.all(), slug_field="slug")
    promocode = serializers.CharField(required=False)
    desired_bank = serializers.ChoiceField(choices=BANK_CHOICES, required=False)
