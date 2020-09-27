from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

from app.models import DefaultQuerySet, TimestampedModel, models


class PromoCodeQuerySet(DefaultQuerySet):
    def get_or_nothing(self, name):
        try:
            return self.get(name=name)

        except PromoCode.DoesNotExist:
            return None


class PromoCode(TimestampedModel):
    objects = PromoCodeQuerySet.as_manager()

    name = models.CharField(_('Promo Code'), max_length=32, unique=True, db_index=True)
    discount_percent = models.IntegerField(_('Discount percent'))
    active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Promo Code')
        verbose_name_plural = _('Promo Codes')

    def apply(self, price: Decimal) -> Decimal:
        return Decimal(price * (100 - self.discount_percent) / 100)
