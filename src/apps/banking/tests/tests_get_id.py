import pytest

from apps.banking.b2b import B2BBank
from apps.banking.exceptions import BankDoesNotExist
from apps.banking.selector import get_id
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBankKZT, StripeBankUSD
from apps.tinkoff.bank import TinkoffBank


@pytest.mark.parametrize(
    ("id", "bank_class"),
    [
        ("tinkoff_bank", TinkoffBank),
        ("stripe", StripeBankUSD),
        ("stripe_kz", StripeBankKZT),
        ("zero_price", ZeroPriceBank),
        ("b2b", B2BBank),
    ],
)
def test_get_bank_return_bank_class_by_id_or_none_if_empty(id, bank_class):
    assert get_id(bank_class) == id


def test_raise_if_bank_does_not_exists():
    class Ev1l: ...

    with pytest.raises(BankDoesNotExist):
        get_id(Ev1l)
