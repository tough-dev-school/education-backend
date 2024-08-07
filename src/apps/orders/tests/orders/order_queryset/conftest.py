import pytest


@pytest.fixture
def order(factory):
    return factory.order(price=999)
