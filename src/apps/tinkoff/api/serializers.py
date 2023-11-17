from _decimal import Decimal
from rest_framework import serializers

from apps.tinkoff.models import DolyameNotification
from apps.tinkoff.models import PaymentNotification


class PaymentNotificationSerializer(serializers.ModelSerializer):
    TerminalKey = serializers.CharField(source="terminal_key")
    OrderId = serializers.IntegerField(source="order_id")
    Success = serializers.BooleanField(source="success")
    Status = serializers.CharField(source="status")
    PaymentId = serializers.IntegerField(source="payment_id")
    ErrorCode = serializers.CharField(source="error_code", required=False, allow_null=True)
    Amount = serializers.IntegerField(source="amount")
    RebillId = serializers.IntegerField(source="rebill_id", required=False, allow_null=True)
    CardId = serializers.CharField(source="card_id", required=False, allow_null=True, allow_blank=True)
    Pan = serializers.CharField(source="pan", required=False, allow_null=True)
    DATA = serializers.CharField(source="data", required=False, allow_null=True)
    Token = serializers.CharField(source="token")
    ExpDate = serializers.CharField(source="exp_date", required=False, allow_null=True)

    class Meta:
        model = PaymentNotification
        fields = [
            "TerminalKey",
            "OrderId",
            "Success",
            "Status",
            "PaymentId",
            "ErrorCode",
            "Amount",
            "RebillId",
            "CardId",
            "Pan",
            "DATA",
            "Token",
            "ExpDate",
        ]

    def validate_Amount(self, validated_data: int) -> Decimal:
        return Decimal(validated_data / 100)


class DolyameNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DolyameNotification
        fields = [
            "order",
            "status",
            "amount",
            "demo",
            "residual_amount",
            "client_info",
            "payment_schedule",
        ]
