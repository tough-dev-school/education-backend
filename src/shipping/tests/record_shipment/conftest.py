import pytest

from shipping.shipments import RecordShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course', name='Кройка и шитьё', name_genitive='Кройки и шитья')


@pytest.fixture
def record(mixer, course):
    return mixer.blend('courses.Record', course=course)


@pytest.fixture
def shipment(record):
    return RecordShipment(record)
