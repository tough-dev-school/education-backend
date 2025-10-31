import contextlib
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from django.apps import apps
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise


class CurrencyCodes(Enum):
    RUB = "RUB", _("RUB"), "₽"
    USD = "USD", _("USD"), "$"
    EUR = "EUR", _("EUR"), "€"
    KZT = "KZT", _("KZT"), "₸"
    KIS = "KIS", _("KIS (for zero-price orders)"), "💋"

    @classmethod
    def choices(cls) -> tuple[tuple[str, "_StrPromise"], ...]:
        currencies = [(member.name, member.value[1]) for member in cls if member if member.name.isupper()]

        return tuple(currencies)


def get_symbol(code: str) -> str:
    symbol = getattr(CurrencyCodes, code.upper())

    if symbol is None:
        raise ValueError("Non-existant currency symbol")

    return symbol.value[2]


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
