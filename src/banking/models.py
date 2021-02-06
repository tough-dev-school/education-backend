from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models
from banking.selector import BankSelector


class Credit(TimestampedModel):
    STATUSES = (
        ('new', _('New')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('canceled', _('Canceled')),
        ('signed', _('Signed')),
    )
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE)
    bank = models.CharField(_('Bank id'), max_length=32, choices=BankSelector.get_bank_choices(), db_index=True)
    bank_request_id = models.CharField(_('Internal bank request id'), max_length=256, db_index=True)
    status = models.CharField(max_length=32, choices=STATUSES, default='new', db_index=True)

    class Meta:
        verbose_name = _('Bank credit')
        verbose_name_plural = _('Bank credits')

        constraints = [
            models.UniqueConstraint(fields=['order', 'bank', 'bank_request_id'], name='Single request to single bank within one order'),
        ]

        indexes = [
            models.Index(fields=['order', 'bank', 'bank_request_id']),
        ]
