import pytest


@pytest.fixture
def customer(mixer):
    return mixer.blend("b2b.Customer")


@pytest.fixture
def course(factory):
    return factory.course(name="Стать CTO")
