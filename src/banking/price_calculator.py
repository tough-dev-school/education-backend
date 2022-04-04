from typing import Type

from decimal import Decimal

from banking.base import Bank
from banking.selector import BankSelector


def to_bank(bank: Type[Bank], price: Decimal) -> Decimal:
    exchanged_price = Decimal(price / bank.ue)

    if not price % 1:  # initial price contains decimal part, e.g. kopecks
        exchanged_price = Decimal(round(exchanged_price))

    return Decimal(round(exchanged_price, 2))


def ue_rate_by_bank_name(bank_name: str) -> int:
    if bank_name not in BankSelector.banks:
        raise KeyError(f'Bank not found: {bank_name}')

    Bank = BankSelector()(bank_name)

    return Bank.ue
