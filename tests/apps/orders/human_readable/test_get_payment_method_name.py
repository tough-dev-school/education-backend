from datetime import datetime
import pytest

from apps.banking.selector import BANK_KEYS
from apps.banking.selector import BANKS
from apps.orders import human_readable

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _set_en_locale(settings):
    settings.LANGUAGE_CODE = "en"


@pytest.fixture
def set_order_paid(order, user):
    def set_paid(bank_id):
        order.paid = datetime.fromisoformat("2023-08-10 09:10:+03:00")
        order.bank_id = bank_id

        order.user = user
        order.author = user

        order.save()
        return order

    return set_paid


def test_readable_payment_method_name_not_paid_order(order):
    got = human_readable.get_order_payment_method_name(order)

    assert got == "—"


def test_get_readable_payment_method_name_shipped_but_not_paid(order):
    order.setattr_and_save("shipped", datetime.fromisoformat("2023-09-13 10:20+03:00"))

    got = human_readable.get_order_payment_method_name(order)

    assert got == "Shipped without payment"


@pytest.mark.parametrize("bank_id", BANK_KEYS)
def test_get_readable_payment_method_name_if_payed_with_bank(bank_id, set_order_paid):
    order = set_order_paid(bank_id)

    got = human_readable.get_order_payment_method_name(order)

    assert got == BANKS[bank_id].name


def test_get_readable_payment_method_name_if_bank_is_set_but_unknown(set_order_paid):
    order = set_order_paid(bank_id="tinkoff_credit")  #  bank that existed but is no longer in use

    got = human_readable.get_order_payment_method_name(order)

    assert got == "Is paid"
