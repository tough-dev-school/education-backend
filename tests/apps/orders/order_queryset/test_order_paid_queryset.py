import pytest

from django.utils import timezone

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("paid", "is_present"),
    [
        (None, False),
        (timezone.now(), True),
    ],
)
def test_true(order, paid, is_present):
    order.update(paid=paid)

    assert (order in Order.objects.paid()) is is_present


@pytest.mark.parametrize(
    ("paid", "is_present"),
    [
        (None, True),
        (timezone.now(), False),
    ],
)
def test_invert(order, paid, is_present):
    order.update(paid=paid)

    assert (order in Order.objects.paid(invert=True)) is is_present
