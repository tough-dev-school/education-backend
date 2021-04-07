import pytest


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', price=100500)
