from typing import Type

from banking.base import Bank
from banking.zero_price_bank import ZeroPriceBank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit
from tinkoff.dolyame import Dolyame

BANKS = {
    "tinkoff_bank": TinkoffBank,
    "tinkoff_credit": TinkoffCredit,
    "stripe": StripeBank,
    "dolyame": Dolyame,
    "zero_price": ZeroPriceBank,
}

BANK_CHOICES = tuple(BANKS.keys())

DEFAULT_BANK = TinkoffBank


def get_bank(desired: str | None = None) -> Type[Bank]:
    if desired is None:
        return DEFAULT_BANK

    try:
        return BANKS[desired]  # type: ignore
    except KeyError:
        return DEFAULT_BANK


__all__ = [
    "get_bank",
]
