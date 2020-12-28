import pytest
from decimal import Decimal

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('testcode'),
]


def get_order():
    return Order.objects.last()


@pytest.mark.parametrize('promocode, expected', [
    ('TESTCODE', 1710),
    ('', 1900),
    ('3V1L_H4XX0R', 1900),
])
def test_purchasing_with_promocode(api, course, promocode, expected):
    api.post(f'/api/v2/courses/{course.slug}/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'promocode': promocode,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.item == course
    assert placed.price == Decimal(expected)


def test_promocode_is_stored(api, course, testcode):
    api.post(f'/api/v2/courses/{course.slug}/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'promocode': 'TESTCODE',
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.promocode == testcode


def test_promocode_is_empty_when_no_promocode_supplied(api, course):
    api.post(f'/api/v2/courses/{course.slug}/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.promocode is None
