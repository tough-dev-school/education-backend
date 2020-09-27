from decimal import Decimal

import pytest

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
def test_(api, course, promocode, expected):
    api.post('/api/v2/courses/ruloning-oboev/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'promocode': promocode,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.item == course
    assert placed.price == Decimal(expected)
