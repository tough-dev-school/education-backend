from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(name="Запись курсов кройки и шитья", price=100500)


@pytest.fixture(autouse=True)
def test_promocode(mixer):
    return mixer.blend("orders.PromoCode", name="TESTCODE", discount_percent=10)


def test_get_price(course):
    assert course.get_price() == Decimal("100500.00")


@pytest.mark.parametrize(
    ("promocode", "expected"),
    [
        ("TESTCODE", "90450"),
        ("testcode", "90450"),
        (None, "100500"),
        ("NONEXISTANT_PROMO_CODE_FROM_EV1L_H4XX0R", "100500"),
    ],
)
def test_get_price_with_promocode(course, promocode, expected):
    assert course.get_price(promocode=promocode) == Decimal(expected)
