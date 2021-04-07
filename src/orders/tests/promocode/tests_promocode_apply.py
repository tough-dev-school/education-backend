import pytest
from decimal import Decimal

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(course):
    course.setattr_and_save('price', 100)
    return course


@pytest.mark.parametrize(('discount_percent', 'expected'), [
    ('50', 50),
    ('25', 75),
    ('0', 100),
    ('100', 0),
])
def test(discount_percent, expected, course, mixer):
    promocode = mixer.blend('orders.PromoCode', discount_percent=discount_percent)

    assert promocode.apply(course) == Decimal(expected)
