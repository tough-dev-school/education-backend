import pytest
from datetime import datetime

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def order(order):
    order.paid = datetime(2032, 12, 1, 15, 30)
    order.save()

    return order


def test_works(order):
    order.set_not_paid()
    order.refresh_from_db()

    assert order.paid is None
    assert order.shipped is None


def test_unships(order, record, user, unship):
    order.set_not_paid()

    unship.assert_called_once_with(order=order)


def test_not_unships_if_order_is_already_paid(order, unship):
    order.setattr_and_save('paid', None)

    order.set_not_paid()

    unship.assert_not_called()


def test_empty_item_does_not_break_things(order, unship):
    order.setattr_and_save('record', None)

    order.set_not_paid()

    unship.assert_not_called()
