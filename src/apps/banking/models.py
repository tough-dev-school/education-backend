from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class CurrencyRate(TimestampedModel):
    class Currency(TextChoices):
        RUB = "RUB", _("RUB")
        USD = "USD", _("USD")
        KZT = "KZT", _("KZT")
        KIS = "KIS", _("KIS (for zero-price orders)")

    name = models.CharField(max_length=4, unique=True, choices=Currency.choices, db_index=True)
    rate = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Rate"))

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")


class AcquiringPercent(TimestampedModel):
    slug = models.CharField(max_length=60, unique=True, db_index=True)
    percent = models.DecimalField(_("Percent"), max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = _("Acquiring percent")
        verbose_name_plural = _("Acquiring percents")

    def __str__(self) -> str:
        return self.slug
