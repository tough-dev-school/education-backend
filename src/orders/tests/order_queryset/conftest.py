import pytest


@pytest.fixture
def order(mixer):
    return mixer.blend('orders.Order')
