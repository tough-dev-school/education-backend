from decimal import Decimal

import pytest

from apps.tinkoff.bank import TinkoffBank

pytestmark = [
    pytest.mark.django_db,
]


def test_get_currency_rate(factory):
    factory.currency(name="RUB", rate=Decimal(1050))

    assert TinkoffBank.get_currency_rate() == 1050


def test_default_if_no_currency_rate():
    assert TinkoffBank.get_currency_rate() == Decimal(1)
