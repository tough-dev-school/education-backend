import pytest
from django.utils import timezone

pytestmark = [pytest.mark.django_db]


def test_order_is_shipped_even_if_it_is_not_paid(order, ship, course, user):
    result = order.ship_without_payment()

    assert result is True
    ship.assert_called_once_with(course, to=user, order=order)


def test_order_is_marked_as_shipped_even_if_it_is_not_paid(order):
    order.ship_without_payment()

    order.refresh_from_db()

    assert order.shipped is not None
    assert order.paid is None


def test_not_ships_if_order_is_paid(order, ship):
    order.paid = timezone.now()

    result = order.ship_without_payment()

    assert result is False
    ship.assert_not_called()
