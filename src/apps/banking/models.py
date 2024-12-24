from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from core.models import DefaultModel


class CurrencyRate(DefaultModel):
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
