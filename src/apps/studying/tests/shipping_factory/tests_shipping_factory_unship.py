import pytest

from apps.studying import shipment_factory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def unship_course(mocker):
    return mocker.patch("apps.studying.shipment.CourseShipment.unship")


def test_course(course, unship_course, factory):
    order = factory.order(item=course)
    shipment_factory.unship(order)

    unship_course.assert_called_once()


def test_shipping_stuff_without_registered_shipping_algorithm(factory):
    order = factory.order()  # random order without an item
    order.update(course=None)

    with pytest.raises(shipment_factory.ShipmentAlgorithmNotFound):
        shipment_factory.unship(order)
