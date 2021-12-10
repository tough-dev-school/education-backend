import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship(mocker):
    return mocker.patch('studying.shipment.RecordShipment.ship')


@pytest.fixture
def order(mixer):
    return mixer.blend('orders.Order')


def test_record(record, ship, user, order):
    record.ship(to=user, order=order)

    ship.assert_called_once()
