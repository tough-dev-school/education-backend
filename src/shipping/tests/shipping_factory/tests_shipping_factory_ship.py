import pytest

from shipping import factory

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship(mocker):
    return mocker.patch('shipping.shipments.RecordShipment.ship')


def test_record(record, ship, user):
    factory.ship(record, to=user)

    ship.assert_called_once()


def test_shipping_stuf_without_registered_shipping_algorithm(ship, user):
    with pytest.raises(factory.ShipmentAlgorithmNotFound):
        factory.ship(user, to=user)
