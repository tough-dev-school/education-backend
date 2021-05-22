import pytest

from studying.shipment import RecordShipment

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def record(mixer):
    return lambda template_id: mixer.blend('products.Record', template_id=template_id)


@pytest.fixture
def shipment(user, mixer):
    def _shipment(product):
        order = mixer.blend('orders.Order')
        order.set_item(product)

        return RecordShipment(user=user, product=product, order=order)

    return _shipment


@pytest.mark.parametrize(('template_id', 'expected'), [
    (None, 'purchased-record'),  # the default one
    (100500, '100500'),
])
def test(record, shipment, template_id, expected):
    record = record(template_id=template_id)

    shipment = shipment(record)

    assert shipment.get_template_id() == expected
