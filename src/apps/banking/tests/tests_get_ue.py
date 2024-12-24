import pytest

from apps.banking.base import Bank
from apps.banking.exceptions import CurrencyRateDoesNotExist

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def rub(factory):
    return factory.currency_rate(name="RUB", rate=1)


@pytest.mark.usefixtures("rub")
def test_get_ue():
    assert Bank.get_ue() == 1


def test_raise_if_no_currency_rate():
    with pytest.raises(CurrencyRateDoesNotExist):
        Bank.get_ue()
