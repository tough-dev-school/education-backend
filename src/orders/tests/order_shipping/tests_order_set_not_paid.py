import pytest
from datetime import datetime, timezone

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30+05:00'),
]


@pytest.fixture
def order(order):
    order.set_paid()

    return order


def test_removes_study_record(order):
    order.set_not_paid()
    order.refresh_from_db()

    assert order.paid is None
    assert order.shipped is None
    assert not hasattr(order, 'study'), 'Study record should be deleted at this point'


def test_unships(order, unship):
    order.set_not_paid()

    unship.assert_called_once_with(order=order)


def test_not_unships_if_order_was_not_paid(order, unship):
    order.setattr_and_save('paid', None)

    order.set_not_paid()

    unship.assert_not_called()


def test_empty_item_does_not_break_things(order, unship):
    order.setattr_and_save('course', None)

    order.set_not_paid()

    unship.assert_not_called()


def test_sets_unpaid_date(order):
    order.set_not_paid()

    order.refresh_from_db()

    assert order.unpaid == datetime(2032, 12, 1, 10, 30, tzinfo=timezone.utc)  # -5 hours as timezone delta


def test_does_not_set_unpaid_date_if_order_was_not_paid(order):
    order.setattr_and_save('paid', None)

    order.refresh_from_db()

    assert order.unpaid is None
