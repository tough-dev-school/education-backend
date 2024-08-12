from typing import Type

from apps.banking.base import Bank
from apps.banking.exceptions import BankDoesNotExist
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBankKZT, StripeBankUSD
from apps.tinkoff.bank import TinkoffBank
from apps.tinkoff.dolyame import Dolyame

BANKS: dict[str, Type[Bank]] = {
    "tinkoff_bank": TinkoffBank,
    "stripe": StripeBankUSD,
    "stripe_kz": StripeBankKZT,
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


def get_bank_or_default(desired: str | None = None) -> Type[Bank]:
    if desired is None:
        return DEFAULT_BANK

    try:
        return BANKS[desired]
    except KeyError:
        return DEFAULT_BANK


def get_bank(bank_id: str) -> Type[Bank] | None:
    if not bank_id:
        return None

    Bank = BANKS.get(bank_id)

    if Bank is None:
        raise BankDoesNotExist(f"The bank with id '{bank_id}' does not exists.")

    return Bank


__all__ = [
    "get_bank",
]
