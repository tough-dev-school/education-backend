import contextlib
from decimal import Decimal

from django.apps import apps
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class CurrencyCodes(TextChoices):
    RUB = "RUB", _("RUB")
    USD = "USD", _("USD")
    KZT = "KZT", _("KZT")
    KIS = "KIS", _("KIS (for zero-price orders)")


def get_rate(name: str) -> Decimal | None:
    Currency = apps.get_model("banking.Currency")

    with contextlib.suppress(Currency.DoesNotExist):
        return Currency.objects.get(name=name).rate


def get_rate_or_default(name: str) -> Decimal:
    return get_rate(name) or Decimal(1)


__all__ = [
    "CurrencyCodes",
    "get_rate",
    "get_rate_or_default",
]
