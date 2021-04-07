import pytest
from decimal import Decimal

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('testcode'),
]


def get_order():
    return Order.objects.last()


@pytest.mark.parametrize(('promocode', 'expected'), [
    ('TESTCODE', 1710),
    ('', 1900),
    ('3V1L_H4XX0R', 1900),
])
def test_purchasing_with_promocode(call_purchase, record, promocode, expected):
    call_purchase(promocode=promocode)

    placed = get_order()

    assert placed.item == record
    assert placed.price == Decimal(expected)


def test_purchasing_with_promocode_attached_to_courses(call_purchase, mixer, testcode):
    """We need this test just to write down that promocodes attaching
    does not support products, other then courses, and it does not break
    regular purchase
    """
    testcode.courses.add(mixer.blend('products.Course'))

    call_purchase(promocode='TESTCODE')
    placed = get_order()

    assert placed.price == Decimal(1900)


def test_promocode_is_stored(call_purchase, testcode):
    call_purchase(promocode='TESTCODE')

    placed = get_order()

    assert placed.promocode == testcode


def test_promocode_is_empty_when_no_promocode_supplied(call_purchase, record):
    call_purchase()

    placed = get_order()

    assert placed.promocode is None
