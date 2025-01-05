from typing import TYPE_CHECKING, Type

from apps.banking.base import Bank
from apps.banking.exceptions import BankDoesNotExist
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBankKZT, StripeBankUSD
from apps.tinkoff.bank import TinkoffBank
from apps.tinkoff.dolyame import Dolyame

if TYPE_CHECKING:
    from django_stubs_ext import StrPromise


BANKS: list[Type[Bank]] = [
    TinkoffBank,
    StripeBankUSD,
    StripeBankKZT,
    Dolyame,
    ZeroPriceBank,
]

BANKS_MAPPING: dict[str, Type[Bank]] = {bank.bank_id: bank for bank in BANKS}
BANK_KEYS = sorted(BANKS_MAPPING.keys())
BANK_CHOICES: list[tuple[str, "StrPromise"]] = [(key, BANKS_MAPPING[key].name) for key in BANK_KEYS]

DEFAULT_BANK = TinkoffBank


def get_bank_or_default(desired: str | None = None) -> Type[Bank]:
    if desired is None:
        return DEFAULT_BANK

    try:
        return BANKS_MAPPING[desired]
    except KeyError:
        return DEFAULT_BANK


def get_bank(bank_id: str) -> Type[Bank] | None:
    if not bank_id:
        return None

    Bank = BANKS_MAPPING.get(bank_id)

    if Bank is None:
        raise BankDoesNotExist(f"The bank with id '{bank_id}' does not exists.")

    return Bank


__all__ = [
    "get_bank",
]
