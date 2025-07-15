from decimal import Decimal

import pytest

from apps.stripebank.bank import StripeBankUSD

pytestmark = [
    pytest.mark.django_db,
]


def test_get_currency_rate(factory):
    factory.currency(name="USD", rate=Decimal(1050))

    assert StripeBankUSD.get_currency_rate() == 1050


def test_default_if_no_currency_rate():
    assert StripeBankUSD.get_currency_rate() == Decimal("44.5")
