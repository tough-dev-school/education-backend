from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models


class PaymentNotification(TimestampedModel):
    """Notifcation for acquiring order by TinkoffBank"""
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
    card_id = models.CharField(null=True, max_length=64)
    pan = models.CharField(max_length=128, null=True)
    data = models.TextField(null=True)
    token = models.CharField(max_length=512)
    exp_date = models.CharField(max_length=32, null=True)


class CreditNotification(TimestampedModel):
    """Notification for credit order by TinkoffCredit"""
    STATUS_CHOICES = (
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('canceled', _('Canceled')),
        ('signed', _('Signed')),
    )

    order_id = models.IntegerField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    bank_created = models.DateTimeField()
    first_payment = models.DecimalField(max_digits=10, decimal_places=2)
    order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    product = models.CharField(max_length=128)
    term = models.IntegerField()
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=64, null=True, blank=True)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    middle_name = models.CharField(max_length=32, blank=True, null=True)
    loan_number = models.CharField(max_length=128, blank=True, null=True)
    email = models.CharField(max_length=128, null=True, blank=True)


class DolyameNotification(TimestampedModel):
    STATUS_CHOICES = (
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('refunded', _('Refunded')),
        ('canceled', _('Canceled')),
        ('committed', _('Committed')),
        ('wait_for_commit', _('Waiting for commit')),
        ('completed', _('Completed')),
    )

    order_id = models.CharField(max_length=256)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    demo = models.BooleanField()
    residual_amount = models.DecimalField(max_digits=10, decimal_places=2)
    client_info = models.JSONField(default=dict)
    payment_schedule = models.JSONField(default=dict)
