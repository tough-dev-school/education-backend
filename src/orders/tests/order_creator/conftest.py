import pytest

from orders.services.order_creator import OrderCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def create():
    return lambda *args, **kwargs: OrderCreator(*args, **kwargs)()
