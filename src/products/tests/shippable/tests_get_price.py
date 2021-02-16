import pytest
from decimal import Decimal

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(mixer):
    return mixer.blend('products.Record', name='Запись курсов кройки и шитья', price=100500)


@pytest.fixture(autouse=True)
def test_promocode(mixer):
    return mixer.blend('orders.PromoCode', name='TESTCODE', discount_percent=10)


def test_get_price(record):
    assert record.get_price() == Decimal('100500.00')


@pytest.mark.parametrize(('promocode', 'expected'), [
    ('TESTCODE', '90450'),
    ('testcode', '90450'),
    (None, '100500'),
    ('NONEXISTANT_PROMO_CODE_FROM_EV1L_H4XX0R', '100500'),
])
def test_get_price_with_promocode(record, promocode, expected):
    assert record.get_price(promocode=promocode) == Decimal(expected)
