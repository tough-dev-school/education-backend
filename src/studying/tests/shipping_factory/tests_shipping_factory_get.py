import pytest

from studying import shipment_factory as factory
from studying.shipment import CourseShipment

pytestmark = [pytest.mark.django_db]


def test_course(course):
    assert factory.get(course) == CourseShipment


def test_non_found(mixer, user):
    """Shipping some non-shippable stuf ergo stuff without a registered shipment"""
    with pytest.raises(factory.ShipmentAlgorithmNotFound):
        factory.get(user)
