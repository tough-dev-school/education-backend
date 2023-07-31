from rest_framework import serializers


class PromocodeSerializer(serializers.Serializer):
    price = serializers.IntegerField()
    formatted_price = serializers.CharField()
    currency = serializers.CharField()
    currency_symbol = serializers.CharField()
