from datetime import datetime
import pytest

from banking.selector import BANK_CHOICES
from banking.selector import BANKS

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _set_en_locale(settings):
    settings.LANGUAGE_CODE = "en"


@pytest.fixture
def order(factory, course, user):
    order = factory.order(user=user, price=1500)
    order.set_item(course)

    return order


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


def test_get_payment_method_not_paid_order(order):
    got = order.get_payment_method()

    assert got == "—"


def test_get_payment_method_shipped_but_not_paid(order):
    order.setattr_and_save("shipped", datetime.fromisoformat("2023-09-13 10:20+03:00"))

    got = order.get_payment_method()

    assert got == "Shipped without payment"


@pytest.mark.parametrize("bank_id", BANK_CHOICES)
def test_get_payment_method_if_payed_with_bank(bank_id, set_order_paid):
    order = set_order_paid(bank_id)

    got = order.get_payment_method()

    assert got == BANKS[bank_id].name


def test_get_payment_method_if_paid_b2b(b2b_order):
    got = b2b_order.get_payment_method()

    assert got == "B2B"


def test_get_payment_method_if_bank_not_set_and_not_b2b(set_order_paid):
    order = set_order_paid(bank_id="")

    got = order.get_payment_method()

    assert got == "Is paid"
