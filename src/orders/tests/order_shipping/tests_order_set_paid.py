import pytest
from datetime import datetime, timedelta, timezone

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30+03:00'),
]


def test_works(order):
    assert order.paid is None

    order.set_paid()
    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30, tzinfo=timezone(timedelta(hours=3)))
    assert order.study is not None


def test_ships(order, course, user, ship):
    order.set_paid()

    ship.assert_called_once_with(course, to=user, order=order)


def test_not_ships_if_order_is_already_paid(order, ship):
    order.setattr_and_save('paid', datetime(2032, 12, 1, 15, 30, tzinfo=timezone(timedelta(hours=3))))

    order.set_paid()

    ship.assert_not_called()


def test_not_ships_if_order_has_desired_shipment_date(order, ship):
    order.setattr_and_save('desired_shipment_date', datetime(2039, 12, 12, 15, 30, tzinfo=timezone(timedelta(hours=3))))

    order.set_paid()

    ship.assert_not_called()


def test_orders_with_desired_shipment_date_do_not_have_shipment_date_set(order, ship):
    order.setattr_and_save('desired_shipment_date', datetime(2039, 12, 12, 15, 30, tzinfo=timezone(timedelta(hours=3))))

    order.set_paid()
    order.refresh_from_db()

    assert order.shipped is None


def test_shipment_date(order):
    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2032, 12, 1, 15, 30, tzinfo=timezone(timedelta(hours=3)))


def test_order_is_not_shipped_again_if_already_shipped(order, ship):
    order.shipped = datetime(2000, 11, 12, 1, 13, tzinfo=timezone(timedelta(hours=3)))
    order.save()

    order.set_paid()

    ship.assert_not_called()


def test_shippment_date_is_not_reset(order, ship):
    order.shipped = datetime(2000, 11, 12, 1, 13, tzinfo=timezone(timedelta(hours=3)))
    order.save()

    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2000, 11, 12, 1, 13, tzinfo=timezone(timedelta(hours=3)))


def test_unpaid_date_is_reset(order):
    order.unpaid = datetime(2032, 12, 1, 15, 13, tzinfo=timezone(timedelta(hours=3)))
    order.save()

    order.set_paid()
    order.refresh_from_db()

    assert order.unpaid is None


def test_unpaid_date_is_not_reset_when_order_is_not_paid(order):
    order.paid = datetime(2032, 12, 1, 12, 13, tzinfo=timezone(timedelta(hours=3)))
    order.unpaid = datetime(2032, 12, 1, 15, 13, tzinfo=timezone(timedelta(hours=3)))
    order.save()

    order.set_paid()
    order.refresh_from_db()

    assert order.unpaid == datetime(2032, 12, 1, 15, 13, tzinfo=timezone(timedelta(hours=3))), 'unpaid has not been changed'


def test_empty_item_does_not_break_things(order, ship):
    order.setattr_and_save('course', None)

    order.set_paid()

    ship.assert_not_called()
