import pytest

from banking.selector import BankSelector
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit


@pytest.fixture
def select():
    return BankSelector()


@pytest.mark.parametrize(('desired', 'result'), [
    ('tinkoff_bank', TinkoffBank),
    ('tinkoff_credit', TinkoffCredit),
    ('ev1l', TinkoffBank),
    ('', TinkoffBank),
])
def test(select, desired, result):
    assert select(desired) == result


def test_default_bank(select):
    assert select() == TinkoffBank


def test_choices(select):
    assert select.__class__.get_bank_choices() == (
        ('tinkoff_bank', 'TinkoffBank'),
        ('tinkoff_credit', 'TinkoffCredit'),
    )
