from decimal import Decimal

import pytest


@pytest.fixture
def usd(factory):
    return factory.currency(name="USD", rate=Decimal(100))


@pytest.fixture
def kzt(factory):
    return factory.currency(name="KZT", rate=Decimal(5))
