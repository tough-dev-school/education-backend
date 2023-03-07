import pytest

from banking.selector import get_bank
from banking.zero_price_bank import ZeroPriceBank
from stripebank.bank import StripeBank
from tinkoff.bank import TinkoffBank
from tinkoff.credit import TinkoffCredit


@pytest.mark.parametrize(
    ("desired", "result"),
    [
        ("tinkoff_bank", TinkoffBank),
        ("tinkoff_credit", TinkoffCredit),
        ("stripe", StripeBank),
        ("zero_price", ZeroPriceBank),
        ("ev1l", TinkoffBank),
        ("", TinkoffBank),
    ],
)
def test(desired, result):
    assert get_bank(desired) == result


def test_default_bank():
    assert get_bank() == TinkoffBank
