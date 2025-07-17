from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CurrencyCodes(TextChoices):
    RUB = "RUB", _("RUB")
    USD = "USD", _("USD")
    KZT = "KZT", _("KZT")
    KIS = "KIS", _("KIS (for zero-price orders)")


__all__ = [
    "CurrencyCodes",
]
