import pytest

from apps.banking.selector import get_bank
from apps.banking.deprecated_bank import DeprecatedBank
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBank
from apps.tinkoff.bank import TinkoffBank


@pytest.mark.parametrize(
    ("desired", "result"),
    [
        ("tinkoff_bank", TinkoffBank),
        ("stripe", StripeBank),
        ("zero_price", ZeroPriceBank),
        ("ev1l", TinkoffBank),
        ("", TinkoffBank),
        ("tinkoff_credit", DeprecatedBank),
    ],
)
def test(desired, result):
    assert get_bank(desired) == result


def test_default_bank():
    assert get_bank() == TinkoffBank
