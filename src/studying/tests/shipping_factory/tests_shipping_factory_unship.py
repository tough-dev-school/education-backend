import pytest

from studying import shipment_factory as factory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def unship_record(mocker):
    return mocker.patch('studying.shipment.RecordShipment.unship')


@pytest.fixture
def unship_course(mocker):
    return mocker.patch('studying.shipment.CourseShipment.unship')


def test_record(record, unship_record, mixer):
    order = mixer.blend('orders.Order', record=record)

    factory.unship(order)

    unship_record.assert_called_once()


def test_course(course, unship_course, mixer):
    order = mixer.blend('orders.Order', course=course)
    factory.unship(order)

    unship_course.assert_called_once()


def test_shipping_stuff_without_registered_shipping_algorithm(mixer):
    order = mixer.blend('orders.Order')  # random order without an item

    with pytest.raises(factory.ShipmentAlgorithmNotFound):
        factory.unship(order)
