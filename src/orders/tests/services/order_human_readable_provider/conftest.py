import pytest

from orders.services import OrderHumanReadableProvider

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory, course, user):
    order = factory.order(user=user, price=1500)
    order.set_item(course)

    return order


@pytest.fixture
def provider():
    return OrderHumanReadableProvider()
