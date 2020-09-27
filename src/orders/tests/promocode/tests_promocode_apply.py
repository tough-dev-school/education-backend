from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize('discount_percent, expected', [
    ('50', 50),
    ('25', 75),
    ('0', 100),
    ('100', 0),
])
def test(discount_percent, expected, mixer):
    promocode = mixer.blend('orders.PromoCode', discount_percent=discount_percent)

    assert promocode.apply(100) == Decimal(expected)
