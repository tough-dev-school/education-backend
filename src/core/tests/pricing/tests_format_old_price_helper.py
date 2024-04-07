from decimal import Decimal

import pytest

from core.pricing import format_old_price

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("old_price", "price", "expected"),
    [
        (100, 500, "1̶0̶0̶ 500 ₽"),
        (0, 500, "500 ₽"),
        (100200, 100500, "1̶0̶0̶2̶0̶0̶ 100\xa0500 ₽"),
        ("200.95", 100500, "2̶0̶0̶,̶9̶5̶ 100\xa0500 ₽"),
    ],
)
def test(old_price, price, expected):
    assert format_old_price(Decimal(old_price), Decimal(price)) == expected


def test_None():
    assert format_old_price(None, 500) == "500 ₽"
