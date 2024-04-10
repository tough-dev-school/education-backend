import pytest
from django.utils import timezone

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    ("paid", "is_present"),
    [
        (None, True),
        (timezone.now(), False),
    ],
)
def test_true(order, paid, is_present):
    order.update(paid=paid)

    assert (order in Order.objects.not_paid()) is is_present
