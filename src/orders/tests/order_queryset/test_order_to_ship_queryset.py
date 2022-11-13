import pytest

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 00:15Z'),
]


@pytest.fixture
def order(order):
    order.paid = '2032-12-01 00:01:00Z'
    order.desired_shipment_date = '2032-12-01 00:14:00Z'
    order.shipped = None

    order.save()

    return order


@pytest.mark.parametrize(('modify_order', 'should_be_shipped'), [
    (lambda order: None, True),
    (lambda order: order.update_from_kwargs(paid=None), False),
    (lambda order: order.update_from_kwargs(shipped='2032-12-01 00:01:01Z'), False),
    (lambda order: order.update_from_kwargs(desired_shipment_date='2032-12-01 00:16:00Z'), False),  # not yet to come
    (lambda order: order.update_from_kwargs(desired_shipment_date='2032-12-01 00:15:00Z'), True),
    (lambda order: order.update_from_kwargs(desired_shipment_date=None), False),
])
def test(order, modify_order, should_be_shipped):
    modify_order(order)

    order.save()

    assert (order in Order.objects.to_ship()) is should_be_shipped
