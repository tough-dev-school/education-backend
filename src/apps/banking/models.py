from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import DefaultModel


class CurrencyRate(DefaultModel):
    name = models.CharField(max_length=4, unique=True, help_text=_("Currency name in ISO 4217 format. E.g. USD"))
    rate = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_("Rate"))

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
