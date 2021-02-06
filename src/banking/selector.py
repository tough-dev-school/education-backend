from typing import Optional

from app.banking import Bank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit


class BankSelector:
    """Stub future-proof bank selector"""
    banks = {
        'tinkoff_bank': TinkoffBank,
        'tinkoff_credit': TinkoffCredit,
    }
    default = 'tinkoff_bank'

    def __call__(self, desired_bank: Optional[str] = default) -> Bank:
        return self.banks.get(desired_bank, self.banks[self.default])

    @classmethod
    def get_bank_choices(cls) -> dict:
        return tuple([(key, BankClass.__name__) for key, BankClass in cls.banks.items()])
