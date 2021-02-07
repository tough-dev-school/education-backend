import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(mixer):
    return mixer.blend('orders.Order')
