from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class PaymentNotification(TimestampedModel):
    """Notifcation for acquiring order by TinkoffBank"""

    STATUS_CHOICES = (
        ("AUTHORIZED", _("Authorized")),
        ("CONFIRMED", _("Confirmed")),
        ("REVERSED", _("Reversed")),
        ("REFUNDED", _("Refunded")),
        ("PARTIAL_REFUNDED", _("Partial refunded")),
        ("REJECTED", _("Rejected")),
    )

    terminal_key = models.CharField(max_length=512)
    order = models.ForeignKey("orders.Order", on_delete=models.PROTECT, related_name="tinkoff_payment_notifications")
    success = models.BooleanField()
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    payment_id = models.BigIntegerField()
    error_code = models.CharField(max_length=512, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    rebill_id = models.BigIntegerField(null=True)
    card_id = models.CharField(null=True, max_length=64)
    pan = models.CharField(max_length=128, null=True)
    data = models.TextField(null=True)
    token = models.CharField(max_length=512)
    exp_date = models.CharField(max_length=32, null=True)


class DolyameNotification(TimestampedModel):
    STATUS_CHOICES = (
        ("approved", _("Approved")),
        ("rejected", _("Rejected")),
        ("refunded", _("Refunded")),
        ("canceled", _("Canceled")),
        ("committed", _("Committed")),
        ("wait_for_commit", _("Waiting for commit")),
        ("completed", _("Completed")),
    )

    order = models.ForeignKey("orders.Order", related_name="dolyame_notifications", on_delete=models.PROTECT)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    demo = models.BooleanField()
    residual_amount = models.DecimalField(max_digits=10, decimal_places=2)
    client_info = models.JSONField(default=dict)
    payment_schedule = models.JSONField(default=dict)
