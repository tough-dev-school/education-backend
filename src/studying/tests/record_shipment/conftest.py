import pytest

from studying.shipment import RecordShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(name="Кройка и шитьё", name_genitive="Кройки и шитья")


@pytest.fixture
def record(factory, course):
    return factory.record(course=course)


@pytest.fixture
def order(factory, record):
    return factory.order(item=record)


@pytest.fixture
def shipment(user, record, order):
    return RecordShipment(user=user, product=record, order=order)
