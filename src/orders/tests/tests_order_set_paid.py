from datetime import datetime

import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture(autouse=True)
def ship(mocker):
    return mocker.patch('shipping.factory.ship')


@pytest.fixture
def record(mixer):
    return mixer.blend('courses.Record')


@pytest.fixture
def order(mixer, record, user):
    order = mixer.blend('orders.Order', user=user)
    order.set_item(record)

    return order


def test_works(order):
    assert order.paid is None

    order.set_paid()
    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30)


def test_ships(order, record, user, ship):
    order.set_paid()

    ship.assert_called_once_with(record, to=user)


def test_shipment_date(order):
    order.set_paid()
    order.refresh_from_db()

    assert order.shipped == datetime(2032, 12, 1, 15, 30)


def test_empty_item_does_not_break_things(order, ship):
    order.setattr_and_save('record', None)

    order.set_paid()

    ship.assert_not_called()
