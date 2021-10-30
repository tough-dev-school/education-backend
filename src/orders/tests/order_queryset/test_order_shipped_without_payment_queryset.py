import pytest
from django.utils import timezone

from orders.models import Order

pytestmark = [pytest.mark.django_db]


def test_includes_paid_but_not_shipped_orders(order):
    order.paid = None
    order.shipped = timezone.now()

    order.save()

    assert order in Order.objects.shipped_without_payment()


def test_excludes_paid_and_shipped_orders(order):
    order.paid = timezone.now()
    order.shipped = timezone.now()

    order.save()

    assert order not in Order.objects.shipped_without_payment()


def test_excludes_not_paid_and_not_shipped_orders(order):
    order.paid = None
    order.shipped = None

    order.save()

    assert order not in Order.objects.shipped_without_payment()


def test_excludes_paid_but_not_shipped_orders(order):
    order.paid = timezone.now()
    order.shipped = None

    order.save()

    assert order not in Order.objects.shipped_without_payment()
