import pytest

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 00:15-02:00"),
]


@pytest.fixture
def order(order):
    order.paid = "2032-12-01 00:01:00-02:00"
    order.shipped = None

    order.save()

    return order


@pytest.mark.parametrize(
    ("modify_order", "should_be_shipped"),
    [
        (lambda order: None, True),
        (lambda order: order.update_from_kwargs(paid=None), False),
        (lambda order: order.update_from_kwargs(shipped="2032-12-01 00:01:01-02:00"), False),
    ],
)
def test(order, modify_order, should_be_shipped):
    modify_order(order)

    order.save()

    assert (order in Order.objects.to_ship()) is should_be_shipped
