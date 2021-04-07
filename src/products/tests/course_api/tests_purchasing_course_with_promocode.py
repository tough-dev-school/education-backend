import pytest
from decimal import Decimal

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('testcode'),
]


def get_order():
    return Order.objects.last()


@pytest.fixture
def another_course(mixer):
    return mixer.blend('products.Course', slug='kamazing-navoza', price=100500)


@pytest.mark.parametrize(('promocode', 'expected'), [
    ('TESTCODE', 1710),
    ('', 1900),
    ('3V1L_H4XX0R', 1900),
])
def test_purchasing_with_promocode(call_purchase, course, promocode, expected):
    call_purchase(promocode=promocode)

    placed = get_order()

    assert placed.item == course
    assert placed.price == Decimal(expected)


def test_incompatible_promocode(call_purchase, another_course, testcode):
    testcode.courses.add(another_course)

    call_purchase(promocode='TESTCODE')
    placed = get_order()

    assert placed.price == Decimal('1900')


def test_promocode_is_stored(call_purchase, course, testcode):
    call_purchase(promocode='TESTCODE')

    placed = get_order()

    assert placed.promocode == testcode


def test_promocode_is_empty_when_no_promocode_supplied(call_purchase, course):
    call_purchase()

    placed = get_order()

    assert placed.promocode is None
