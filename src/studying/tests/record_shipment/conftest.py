import pytest

from studying.shipment import RecordShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', name='Кройка и шитьё', name_genitive='Кройки и шитья')


@pytest.fixture
def record(mixer, course):
    return mixer.blend('products.Record', course=course)


@pytest.fixture
def order(factory, record):
    return factory.order(item=record)


@pytest.fixture
def shipment(user, record, order):
    return RecordShipment(user=user, product=record, order=order)
