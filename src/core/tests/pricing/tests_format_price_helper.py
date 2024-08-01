from decimal import Decimal

import pytest

from core.pricing import format_price

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("100500", "100\xa0500"),
        ("100500.95", "100\xa0500,95"),
        ("500.95", "500,95"),
        ("0", "0"),
        ("0.5", "0,5"),
    ],
)
def test(input, expected):
    assert format_price(Decimal(input)) == expected


def test_None():
    assert format_price(None) == "0"
