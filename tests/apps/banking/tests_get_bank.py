import pytest

from apps.banking.selector import get_bank
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.stripebank.bank import StripeBank
from apps.tinkoff.bank import TinkoffBank
from apps.banking.exceptions import BankDoesNotExist
from apps.banking.manual_bank import ManualBank


@pytest.mark.parametrize(
    ("bank_id", "result"),
    [
        ("tinkoff_bank", TinkoffBank),
        ("stripe", StripeBank),
        ("zero_price", ZeroPriceBank),
        ("manual", ManualBank),
    ],
)
def test_get_bank_return_bank_class_by_id(bank_id, result):
    assert get_bank(bank_id) == result


@pytest.mark.parametrize("bank_id", ["", "credit_bank"])
def test_raise_if_bank_id_not_exists_or_empty(bank_id):
    with pytest.raises(BankDoesNotExist):
        get_bank(bank_id)
