from typing import Optional, Type

from banking.base import Bank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit

BANKS = {
    'tinkoff_bank': TinkoffBank,
    'tinkoff_credit': TinkoffCredit,
    'stripe': StripeBank,
}

DEFAULT_BANK = TinkoffBank


def get_bank(desired: Optional[str] = None) -> Type[Bank]:
    if desired is None:
        return DEFAULT_BANK

    try:
        return BANKS[desired]
    except KeyError:
        return DEFAULT_BANK


__all__ = [
    'get_bank',
]
