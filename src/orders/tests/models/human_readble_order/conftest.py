import pytest

from orders.models import HumanReadableOrder

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def readable_order(factory, course, user):
    order = factory.order(user=user, price=1500)
    order.set_item(course)

    return HumanReadableOrder.objects.get(id=order.id)
