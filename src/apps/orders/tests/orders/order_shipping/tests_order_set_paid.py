from datetime import datetime, timezone

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30Z"),
]


def test_works(order):
    assert order.paid is None

    order.set_paid()
    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)
    assert order.study is not None


def test_ships(order, course, user, ship):
    order.set_paid()

    ship.assert_called_once_with(course, to=user, order=order)


def test_not_ships_if_order_is_already_paid(order, ship):
    order.update(paid=datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc))

    order.set_paid()

    ship.assert_not_called()


def test_shipment_date(order):
    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc)


def test_order_is_not_shipped_again_if_already_shipped(order, ship):
    order.update(shipped=datetime(2032, 12, 1, 15, 30, tzinfo=timezone.utc))

    order.set_paid()

    ship.assert_not_called()


def test_shipment_date_is_not_reset(order):
    order.update(shipped=datetime(2000, 11, 12, 1, 13, tzinfo=timezone.utc))

    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2000, 11, 12, 1, 13, tzinfo=timezone.utc)


def test_empty_item_does_not_break_things(order, ship):
    order.update(course=None)

    order.set_paid()

    ship.assert_not_called()
