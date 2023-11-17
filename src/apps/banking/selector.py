from typing import Type

from apps.banking.base import Bank
from apps.banking.deprecated_bank import DeprecatedBank
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBank
from apps.tinkoff.bank import TinkoffBank
from apps.tinkoff.dolyame import Dolyame

BANKS: dict[str, Type[Bank]] = {
    "tinkoff_bank": TinkoffBank,
    "stripe": StripeBank,
    "dolyame": Dolyame,
    "zero_price": ZeroPriceBank,
    "tinkoff_credit": DeprecatedBank,
}


BANK_KEYS = sorted(BANKS.keys())
BANK_CHOICES = [
    (
        bank_key,
        BANKS[bank_key].name,
    )
    for bank_key in BANK_KEYS
]
ACTIVE_BANK_CHOICES = [
    (
        bank_key,
        BANKS[bank_key].name,
    )
    for bank_key in BANK_KEYS
    if BANKS[bank_key] != DeprecatedBank
]

DEFAULT_BANK = TinkoffBank


def get_bank(desired: str | None = None) -> Type[Bank]:
    if desired is None:
        return DEFAULT_BANK

    try:
        return BANKS[desired]
    except KeyError:
        return DEFAULT_BANK


__all__ = [
    "get_bank",
]
