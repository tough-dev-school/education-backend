import pytest

from orders.creator import OrderCreator
from orders.models import Order

pytestmark = [pytest.mark.django_db]


def get_order():
    return Order.objects.last()


def create(*args, **kwargs):
    return OrderCreator(*args, **kwargs)()


@pytest.fixture(autouse=True)
def testcode(mixer):
    return mixer.blend('orders.Promocode', name='TESTCODE', discount_percent=10)


@pytest.mark.parametrize('promocode, expected', [
    ('TESTCODE', 90450),
    ('', 100500),
    ('3V1l', 100500),
])
def test(promocode, expected, user, course):
    order = create(user=user, item=course, promocode=promocode)

    order.refresh_from_db()

    assert order.price == expected
