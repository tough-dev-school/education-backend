from decimal import Decimal
from typing import Type

from apps.banking.base import Bank


def to_bank(bank: Type[Bank], price: Decimal) -> Decimal:
    """Get sum in bank currency"""
    exchanged_price = Decimal(price) / Decimal(bank.ue)

    if not price % 1:  # initial price contains decimal part, e.g. kopecks
        exchanged_price = Decimal(round(exchanged_price))

    return round(exchanged_price, 2)
