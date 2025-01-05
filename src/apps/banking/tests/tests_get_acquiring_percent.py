from decimal import Decimal

import pytest

from apps.banking.base import Bank
from apps.banking.exceptions import AcquiringDoesNotExist

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def acquiring_percent(factory):
    return factory.acquiring(bank=Bank.bank_id, percent=Decimal("5.55"))


@pytest.mark.usefixtures("acquiring_percent")
def test_get_acquiring_percent():
    assert Bank.get_acquiring_percent() == Decimal("5.55")


def test_raise_if_no_acquiring_percent():
    with pytest.raises(AcquiringDoesNotExist):
        Bank.get_acquiring_percent()
