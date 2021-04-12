import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def record(mixer):
    return mixer.blend('products.Record')


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle')


@pytest.fixture
def order(mixer, bundle):
    order = mixer.blend('orders.Order')
    order.set_item(bundle)
    order.save()

    return order
