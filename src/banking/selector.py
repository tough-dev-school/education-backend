from typing import Optional, Type

from banking.base import Bank
from banking.definitions import BankChoice
from banking.zero_price_bank import ZeroPriceBank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit
from tinkoff.dolyame import Dolyame

BANKS = {
    BankChoice.TINKOFF_BANK.value: TinkoffBank,
    BankChoice.TINKOFF_CREDIT.value: TinkoffCredit,
    BankChoice.STRIPE.value: StripeBank,
    BankChoice.DOLYAME.value: Dolyame,
    BankChoice.ZERO_PRICE.value: ZeroPriceBank,
}

DEFAULT_BANK = BankChoice.TINKOFF_BANK


def get_bank(desired: Optional[str] = None) -> Type[Bank]:
    if desired is None:
        return BANKS[DEFAULT_BANK]

    try:
        return BANKS[desired]
    except KeyError:
        return BANKS[DEFAULT_BANK]


__all__ = [
    'get_bank',
]
