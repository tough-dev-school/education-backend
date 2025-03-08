import pytest


@pytest.fixture
def customer(mixer):
    return mixer.blend("b2b.Customer")


@pytest.fixture
def another_customer(mixer):
    return mixer.blend("b2b.Customer")


@pytest.fixture
def course(factory):
    return factory.course(name="Стать CTO")


@pytest.fixture
def deal(factory, customer, course):
    return factory.deal(customer=customer, course=course)


@pytest.fixture
def another_deal(factory, customer, course):
    return factory.deal(customer=customer, course=course)
