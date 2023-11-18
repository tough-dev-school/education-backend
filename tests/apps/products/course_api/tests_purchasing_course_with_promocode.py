from decimal import Decimal
import pytest

from apps.orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("testcode"),
]


def get_order():
    return Order.objects.last()


@pytest.fixture
def another_course(factory):
    return factory.course(slug="kamazing-navoza", price=100500)


@pytest.mark.parametrize(
    ("promocode", "expected"),
    [
        ("TESTCODE", 1710),
        ("", 1900),
        ("3V1L_H4XX0R", 1900),
    ],
)
def test_purchasing_with_promocode(call_purchase, course, promocode, expected):
    call_purchase(promocode=promocode)

    placed = get_order()

    assert placed.item == course
    assert placed.price == Decimal(expected)


def test_incompatible_promocode(call_purchase, another_course, testcode):
    testcode.courses.add(another_course)

    call_purchase(promocode="TESTCODE")
    placed = get_order()

    assert placed.price == Decimal("1900"), "promocode should not be accepteed"


@pytest.mark.freeze_time("2032-12-01 23:59")
def test_expired_promocode(call_purchase, testcode):
    testcode.update(expires="2032-11-01 15:30:00+02:00")

    call_purchase(promocode="TESTCODE")
    placed = get_order()

    assert placed.price == Decimal("1900"), "promocode should not be accepteed"


def test_promocode_is_stored(call_purchase, testcode):
    call_purchase(promocode="TESTCODE")

    placed = get_order()

    assert placed.promocode == testcode


def test_promocode_is_empty_when_no_promocode_supplied(call_purchase):
    call_purchase()

    placed = get_order()

    assert placed.promocode is None
