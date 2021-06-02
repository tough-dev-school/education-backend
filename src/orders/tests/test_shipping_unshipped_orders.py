import pytest
from datetime import datetime

from orders import tasks

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 00:15:00'),
]


@pytest.fixture
def product(mixer):
    return mixer.blend('products.Record')


@pytest.fixture
def order(factory, product, another_user):
    return factory.order(
        paid='2032-12-01 00:01:00',
        desired_shipment_date='2032-12-01 00:14:00',
        shipped=None,
        record=product,
        giver=another_user,
        notification_to_giver_is_sent=True,
    )


@pytest.fixture()
def ship(mocker):
    return mocker.patch('studying.shipment_factory.ship')


@pytest.fixture(autouse=True)
def send_happiness_message(mocker):
    return mocker.patch('app.tasks.send_happiness_message.delay')


def test_works(order, ship, product):
    tasks.ship_unshipped_orders()

    ship.assert_called_once_with(product, to=order.user, order=order)


def test_only_receiver_gets_notified_during_gift_shipment(order, send_mail):
    tasks.ship_unshipped_orders()

    send_mail.assert_called_once()


def test_order_is_marked_as_shipped(order):
    assert order.shipped is None

    tasks.ship_unshipped_orders()
    order.refresh_from_db()

    assert order.shipped == datetime(2032, 12, 1, 0, 15)


@pytest.mark.parametrize('change_order', [
    lambda order: order.setattr_and_save('paid', None),
    lambda order: order.setattr_and_save('shipped', '2032-12-01 12:30'),
    lambda order: order.setattr_and_save('desired_shipment_date', None),
])
def test_not_shipping_orders_that_should_not_be_shipped(order, ship, change_order):
    change_order(order)

    tasks.ship_unshipped_orders()

    ship.assert_not_called()


def test_orders_are_shipped_silently(order, send_happiness_message, settings):
    settings.HAPPINESS_MESSAGES_CHAT_ID = 'aaa100500'

    tasks.ship_unshipped_orders()

    send_happiness_message.assert_not_called()
