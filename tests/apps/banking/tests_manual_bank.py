import pytest
from contextlib import nullcontext as does_not_raise
from apps.banking.manual_bank import ManualBank
from apps.orders.models import Order
from rest_framework.exceptions import ValidationError

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory):
    return factory.order(bank_id="manual")


@pytest.fixture
def manual_bank(order):
    return ManualBank(order)


def test_could_be_refunded(manual_bank):
    with does_not_raise():
        manual_bank.refund()


def test_raise_if_try_to_get_initial_payment_url(manual_bank):
    with pytest.raises(ValidationError):
        manual_bank.get_initial_payment_url()
