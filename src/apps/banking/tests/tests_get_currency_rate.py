import pytest

from apps.banking.base import Bank
from apps.banking.exceptions import CurrencyRateDoesNotExist
from apps.banking.models import CurrencyRate

pytestmark = [pytest.mark.django_db]


def test_get_currency_rate():
    assert Bank.get_currency_rate() == 1


def test_raise_if_no_currency_rate():
    CurrencyRate.objects.all().delete()
    with pytest.raises(CurrencyRateDoesNotExist):
        Bank.get_currency_rate()
