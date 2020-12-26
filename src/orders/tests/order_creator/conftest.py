import pytest

from orders.creator import OrderCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def create():
    return lambda *args, **kwargs: OrderCreator(*args, **kwargs)()
