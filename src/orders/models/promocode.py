from django.utils.translation import ugettext_lazy as _

from app.models import TimestampedModel, models


class PromoCode(TimestampedModel):
    name = models.CharField(_('Promo Code'), max_length=32, unique=True, db_index=True)
    discount_percent = models.IntegerField(_('Discount percent'))
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Promo Code')
        verbose_name_plural = _('Promo Codes')
