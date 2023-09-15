from datetime import datetime
import pytest

from banking.selector import BANK_CHOICES
from banking.selector import BANKS
from orders.services import OrderHumanReadableProvider

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


@pytest.fixture
def b2b_order(order, another_user):
    order.bank_id = ""
    order.paid = datetime.fromisoformat("2023-08-10 09:10:+03:00")
    order.user = another_user
    order.save()
    return order


@pytest.fixture
def provider():
    return OrderHumanReadableProvider()


def test_readable_payment_method_name_not_paid_order(order, provider):
    got = provider.get_payment_method_name(order)

    assert got == "—"


def test_get_readable_payment_method_name_shipped_but_not_paid(provider, order):
    order.setattr_and_save("shipped", datetime.fromisoformat("2023-09-13 10:20+03:00"))

    got = provider.get_payment_method_name(order)

    assert got == "Shipped without payment"


@pytest.mark.parametrize("bank_id", BANK_CHOICES)
def test_get_readable_payment_method_name_if_payed_with_bank(provider, bank_id, set_order_paid):
    order = set_order_paid(bank_id)

    got = provider.get_payment_method_name(order)

    assert got == BANKS[bank_id].name


def test_get_readable_payment_method_name_if_paid_b2b(provider, b2b_order):
    got = provider.get_payment_method_name(b2b_order)

    assert got == "B2B"


def test_get_readable_payment_method_name_if_bank_not_set_and_not_b2b(provider, set_order_paid):
    order = set_order_paid(bank_id="")

    got = provider.get_payment_method_name(order)

    assert got == "Is paid"
