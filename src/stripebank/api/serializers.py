from decimal import Decimal

from rest_framework import serializers

from stripebank.bank import StripeBank
from stripebank.models import StripeNotification


class StripeNotificationSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="stripe_id")
    amount_total = serializers.DecimalField(source="amount", decimal_places=2, max_digits=9)
    payment_status = serializers.CharField()
    status = serializers.CharField()
    raw = serializers.JSONField()

    class Meta:
        model = StripeNotification
        fields = [
            "id",
            "order",
            "amount_total",
            "payment_status",
            "status",
            "raw",
        ]

    def validate_amount_total(self, validated_data: Decimal) -> Decimal:
        return Decimal(int(validated_data) / 100 * StripeBank.ue)
