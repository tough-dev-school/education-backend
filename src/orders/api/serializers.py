from rest_framework import serializers

from banking.selector import BANK_CHOICES


class PromocodeSerializer(serializers.Serializer):
    price = serializers.IntegerField()
    formatted_price = serializers.CharField()
    currency = serializers.CharField()
    currency_symbol = serializers.CharField()


class PurchaseSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    desired_bank = serializers.ChoiceField(choices=BANK_CHOICES, required=False)
    promocode = serializers.CharField(max_length=100, required=False)
    success_url = serializers.CharField(max_length=256, required=False)
    redirect_url = serializers.CharField(max_length=256, required=False)
    subscribe = serializers.CharField(max_length=5, required=False)
