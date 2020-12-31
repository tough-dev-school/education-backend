import pytest

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 00:15'),
]


@pytest.fixture
def order(order):
    order.paid = '2032-12-01 00:01:00'
    order.desired_shipment_date = '2032-12-01 00:14:00'
    order.shipped = None

    order.save()

    return order


@pytest.mark.parametrize(('modify_order', 'should_be_shipped'), [
    (lambda order: None, True),
    (lambda order: order.update_from_kwargs(paid=None), False),
    (lambda order: order.update_from_kwargs(shipped='2032-12-01 00:01:01'), False),
    (lambda order: order.update_from_kwargs(desired_shipment_date='2032-12-01 00:16:00'), False),  # not yet to come
    (lambda order: order.update_from_kwargs(desired_shipment_date='2032-12-01 00:15:00'), True),
    (lambda order: order.update_from_kwargs(desired_shipment_date=None), False),
])
def test(order, modify_order, should_be_shipped):
    modify_order(order)

    order.save()

    assert (order in Order.objects.to_ship()) is should_be_shipped
