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
def deal(mixer, customer, course):
    return mixer.blend("b2b.Deal", customer=customer, product=course)


@pytest.fixture
def another_deal(mixer, customer, course):
    return mixer.blend("b2b.Deal", customer=customer, product=course)
