import pytest

from apps.banking.selector import get_bank
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBank
from apps.tinkoff.bank import TinkoffBank
from apps.tinkoff.credit import TinkoffCredit


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
