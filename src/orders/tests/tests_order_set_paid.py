from datetime import datetime

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def order(mixer):
    return mixer.blend('orders.Order')


def test_works(order):
    assert order.paid is None

    order.set_paid()
    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30)
