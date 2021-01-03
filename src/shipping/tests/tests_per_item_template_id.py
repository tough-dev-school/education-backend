import pytest

from shipping.shipments import RecordShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(mixer):
    return lambda template_id: mixer.blend('products.Record', template_id=template_id)


@pytest.fixture
def shipment(user):
    return lambda product: RecordShipment(user, product=product)


@pytest.mark.parametrize('template_id, expected', [
    [None, 'purchased-record'],  # the default one
    [100500, '100500'],
])
def test(record, shipment, template_id, expected):
    record = record(template_id=template_id)

    shipment = shipment(record)

    assert shipment.get_template_id() == expected
