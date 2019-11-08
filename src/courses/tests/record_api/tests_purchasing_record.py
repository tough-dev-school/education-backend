from decimal import Decimal

import pytest

from orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def record(mixer):
    return mixer.blend('courses.Record', slug='home-video')


def get_order():
    return Order.objects.last()


def test_order(api, record):
    api.post('/api/v2/records/home-video/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'price': 1900,
    })

    placed = get_order()

    assert placed.item == record
    assert placed.price == Decimal('1900.00')


def test_user(api, record):
    api.post('/api/v2/records/home-video/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'price': 1900,
    })

    placed = get_order()

    assert placed.user.first_name == 'Забой'
    assert placed.user.last_name == 'Шахтёров'
    assert placed.user.email == 'zaboy@gmail.com'


def test_invalid(api):
    api.post('/api/v2/records/home-video/purchase/', {}, expected_status_code=400)
