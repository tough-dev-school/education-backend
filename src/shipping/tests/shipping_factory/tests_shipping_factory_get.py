import pytest

from shipping import factory
from shipping.shipments import RecordShipment

pytestmark = [pytest.mark.django_db]


def test_record(record):
    assert factory.get(record) == RecordShipment


def test_non_found(mixer, user):
    """Shipping some non-shippable stuf ergo stuff without a registered shipment"""
    with pytest.raises(factory.ShipmentAlgorithmNotFound):
        factory.get(user)
