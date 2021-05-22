import pytest

from orders.services import OrderCreator

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def create():
    return lambda *args, **kwargs: OrderCreator(*args, **kwargs)()
