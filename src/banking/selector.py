from typing import Type

from banking.base import Bank
from banking.zero_price_bank import ZeroPriceBank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit
from tinkoff.dolyame import Dolyame

BANKS: dict[str, Type[Bank]] = {
    "tinkoff_bank": TinkoffBank,
    "tinkoff_credit": TinkoffCredit,
    "stripe": StripeBank,
    "dolyame": Dolyame,
    "zero_price": ZeroPriceBank,
}

BANK_KEYS = sorted(BANKS.keys())
BANK_CHOICES = [
    (
        bank_key,
        BANKS[bank_key].name,
    )
    for bank_key in BANK_KEYS
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
