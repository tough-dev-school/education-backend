import pytest

from banking.selector import get_bank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit


@pytest.mark.parametrize(('desired', 'result'), [
    ('tinkoff_bank', TinkoffBank),
    ('tinkoff_credit', TinkoffCredit),
    ('stripe', StripeBank),
    ('ev1l', TinkoffBank),
    ('', TinkoffBank),
])
def test(desired, result):
    assert get_bank(desired) == result


def test_default_bank():
    assert get_bank() == TinkoffBank
