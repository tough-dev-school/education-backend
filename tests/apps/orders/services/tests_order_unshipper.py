from datetime import datetime, timezone

import pytest

from apps.orders.models import Order
from apps.orders.services import OrderUnshipper

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory, course):
    order = factory.order(item=course, is_paid=True)  # any item should be suitable here
    order.ship()

    Order.objects.update(id=order.id, modified="2021-01-01 23:00Z")
    order.refresh_from_db()

    return order


@pytest.fixture
def mock_item_unshipping(mocker):
    return mocker.patch("apps.studying.shipment_factory.unship")


@pytest.fixture
def unship(order):
    return OrderUnshipper(order=order)


@pytest.mark.freeze_time("2023-01-20 08:00Z")
def test_unshipper_actually_unship_order_and_item_and_nothing_else(order, unship, mock_item_unshipping):
    unship()

    order.refresh_from_db()
    assert order.shipped is None
    assert order.paid is not None, "Should not change on unshipping"
    assert order.modified == datetime(2023, 1, 20, 8, 0, tzinfo=timezone.utc)
    mock_item_unshipping.assert_called_once()


def test_does_not_unship_twice(unship, mock_item_unshipping, mocker):
    mock_order_save = mocker.patch("apps.orders.models.Order.save")
    unship()

    unship()

    mock_order_save.assert_called_once()
    mock_item_unshipping.assert_called_once()


def test_does_not_break_if_item_not_set(order, unship, mock_item_unshipping):
    order.update(course=None)

    unship()

    order.refresh_from_db()
    assert order.shipped is None
    mock_item_unshipping.assert_not_called()
