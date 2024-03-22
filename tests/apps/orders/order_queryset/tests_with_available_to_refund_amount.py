import pytest

from apps.orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


def test_no_refunds(order):
    assert Order.objects.with_available_to_refund_amount().get(pk=order.pk).available_to_refund_amount == 999


def test_with_refunds(order):
    order.refund(100)
    order.refund(150)

    assert Order.objects.with_available_to_refund_amount().get(pk=order.pk).available_to_refund_amount == 749, f"{order.refunds.all()}"
