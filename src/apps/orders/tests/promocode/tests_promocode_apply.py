from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(course):
    return course.update(price=100_500)


@pytest.mark.parametrize(
    ("discount_percent", "expected"),
    [
        ("50", 50_250),
        ("25", 75_375),
        ("0", 100_500),
        ("100", 0),
    ],
)
def test_discount_percent(discount_percent, expected, course, mixer):
    promocode = mixer.blend("orders.PromoCode", discount_percent=discount_percent)

    assert promocode.apply(course) == Decimal(expected)


@pytest.mark.parametrize(
    ("discount_value", "expected"),
    [
        ("50", 100_450),
        ("1", 100_499),
        (0, 100_500),
        (100_600, 100_500),  # greater then the course price
    ],
)
def test_discount_value(discount_value, expected, course, mixer):
    promocode = mixer.blend("orders.PromoCode", discount_percent=None, discount_value=discount_value)

    assert promocode.apply(course) == Decimal(expected)
