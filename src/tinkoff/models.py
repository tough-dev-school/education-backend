from django.utils.translation import ugettext_lazy as _

from app.models import TimestampedModel, models


class PaymentNotification(TimestampedModel):
    STATUS_CHOICES = (
        ('AUTHORIZED', _('Authorized')),
        ('CONFIRMED', _('Confirmed')),
        ('REVERSED', _('Reversed')),
        ('REFUNDED', _('Refunded')),
        ('PARTIAL_REFUNDED', _('Partial refunded')),
        ('REJECTED', _('Rejected')),
    )

    terminal_key = models.CharField(max_length=512)
    order_id = models.IntegerField()
    success = models.BooleanField()
    status = models.CharField(max_length=128, choices=STATUS_CHOICES)
    payment_id = models.BigIntegerField()
    error_code = models.CharField(max_length=512, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    rebill_id = models.BigIntegerField(null=True)
    card_id = models.IntegerField()
    pan = models.CharField(max_length=128, null=True)
    data = models.TextField(null=True)
    token = models.CharField(max_length=512)
    exp_date = models.CharField(max_length=32, null=True)
