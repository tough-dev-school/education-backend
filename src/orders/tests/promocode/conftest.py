import pytest


@pytest.fixture
def course(factory):
    return factory.course(price=100500)


@pytest.fixture
def another_course(factory):
    return factory.course(price=100500)


@pytest.fixture
def ten_percent_promocode(mixer):
    return mixer.blend("orders.PromoCode", discount_percent=10, name="TESTCODE")
