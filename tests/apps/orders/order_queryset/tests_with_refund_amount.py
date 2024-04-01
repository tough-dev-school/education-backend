import time

import pytest

from apps.orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


def test_no_refunds(order):
    assert Order.objects.with_refund_amount().get(pk=order.pk).refund_amount == 0


def test_with_refunds(order):
    order.refund(100)
    time.sleep(10)
    order.refund(150)

    assert Order.objects.with_refund_amount().get(pk=order.pk).refund_amount == 250


def test_only_related_refunds_aggregated(factory, order):
    another_order = factory.order(price=1000)
    order.refund(100)
    another_order.refund(150)

    assert Order.objects.with_refund_amount().get(pk=order.pk).refund_amount == 100
    assert Order.objects.with_refund_amount().get(pk=another_order.pk).refund_amount == 150
