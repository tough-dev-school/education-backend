import pytest

from studying import shipment_factory as factory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship_course(mocker):
    return mocker.patch("studying.shipment.CourseShipment.ship")


def test_course(course, ship_course, user, order):
    factory.ship(course, to=user, order=order)

    ship_course.assert_called_once()


def test_shipping_stuff_without_registered_shipping_algorithm(user, order):
    with pytest.raises(factory.ShipmentAlgorithmNotFound):
        factory.ship({"any rand": "om stuff"}, to=user, order=order)
