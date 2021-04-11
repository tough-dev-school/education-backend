import pytest


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', price=100500)


@pytest.fixture
def another_course(mixer):
    return mixer.blend('products.Course', price=100500)


@pytest.fixture
def promocode(mixer):
    return mixer.blend('orders.PromoCode', discount_percent=10, name='TESTCODE')
