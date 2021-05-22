import pytest

from studying import shipment_factory as factory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship_record(mocker):
    return mocker.patch('studying.shipment.RecordShipment.ship')


@pytest.fixture
def ship_course(mocker):
    return mocker.patch('studying.shipment.CourseShipment.ship')


def test_record(record, ship_record, user):
    factory.ship(record, to=user)

    ship_record.assert_called_once()


def test_course(course, ship_course, user):
    factory.ship(course, to=user)

    ship_course.assert_called_once()


def test_shipping_stuff_without_registered_shipping_algorithm(user):
    with pytest.raises(factory.ShipmentAlgorithmNotFound):
        factory.ship(user, to=user)
