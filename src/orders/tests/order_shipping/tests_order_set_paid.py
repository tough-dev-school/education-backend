from datetime import datetime

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


def test_works(order):
    assert order.paid is None

    order.set_paid()
    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30)


def test_ships(order, record, user, ship):
    order.set_paid()

    ship.assert_called_once_with(record, to=user)


def test_not_ships_if_order_is_already_paid(order, ship):
    order.setattr_and_save('paid', datetime(2032, 12, 1, 15, 30))

    order.set_paid()

    ship.assert_not_called()


def test_not_ships_if_order_has_desired_shipment_date(order, ship):
    order.setattr_and_save('desired_shipment_date', datetime(2039, 12, 12, 15, 30))

    order.set_paid()

    ship.assert_not_called()


def test_shipment_date(order):
    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2032, 12, 1, 15, 30)


def test_empty_item_does_not_break_things(order, ship):
    order.setattr_and_save('record', None)

    order.set_paid()

    ship.assert_not_called()
