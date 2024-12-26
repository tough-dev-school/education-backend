from decimal import Decimal

import pytest

from apps.banking import price_calculator


@pytest.mark.parametrize(
    ("price", "currency_rate", "expected"),
    [
        (100, 1, 100),
        (100.50, 1, 100.50),
        (120, 50, 2),
        (120.2, 50, "2.40"),
        (130, 50, 3),
        (999, 80, 12),
        (999.5, 80, "12.49"),
        (100500, Decimal("0.18"), 558333),
        (100500, Decimal("0.165"), 609091),
        (100500.2, Decimal("0.17"), "591177.65"),
        (100500.5, Decimal("0.17"), "591179.41"),
    ],
)
def test(price, currency_rate, expected):
    class MockBank:
        @classmethod
        def get_currency_rate(cls):
            return currency_rate

    assert price_calculator.to_bank(MockBank, price) == Decimal(expected)
