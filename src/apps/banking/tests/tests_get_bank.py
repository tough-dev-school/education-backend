import pytest

from apps.banking.exceptions import BankDoesNotExist
from apps.banking.selector import get_bank
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBankKZT, StripeBankUSD
from apps.tinkoff.bank import TinkoffBank


@pytest.mark.parametrize(
    ("bank_id", "result"),
    [
        ("tinkoff_bank", TinkoffBank),
        ("stripe", StripeBankUSD),
        ("stripe_kz", StripeBankKZT),
        ("zero_price", ZeroPriceBank),
        ("", None),
    ],
)
def test_get_bank_return_bank_class_by_id_or_none_if_empty(bank_id, result):
    assert get_bank(bank_id) == result


def test_raise_if_bank_id_not_empty_and_not_exists():
    with pytest.raises(BankDoesNotExist):
        get_bank("credit_bank")
