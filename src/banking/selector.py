from typing import Optional, Type

from banking.base import Bank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit


class BankSelector:
    banks = {
        'tinkoff_bank': TinkoffBank,
        'tinkoff_credit': TinkoffCredit,
        'stripe': StripeBank,
    }
    default = 'tinkoff_bank'

    def __call__(self, desired_bank: Optional[str] = None) -> Type[Bank]:
        desired_bank = desired_bank or self.default

        try:
            return self.banks[desired_bank]
        except KeyError:
            return self.banks[self.default]
