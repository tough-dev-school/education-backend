import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(mixer):
    return lambda **kwargs: mixer.blend('orders.Order', **kwargs)
