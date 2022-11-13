import pytest
from datetime import datetime, timezone
from django.conf import settings
from zoneinfo import ZoneInfo

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
]


def get_order():
    return Order.objects.last()


@pytest.fixture
def default_gift_data():
    return {
        'receiver_name': 'Забой Шахтёров',
        'receiver_email': 'zaboy@gmail.com',
        'giver_name': 'Камаз Помоев',
        'giver_email': 'kamaz@gmail.com',
        'desired_shipment_date': '2032-12-01 12:35:15Z',
    }


def test_order(api, course, default_gift_data):
    api.post('/api/v2/courses/ruloning-oboev/gift/', default_gift_data, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.item == course

    assert placed.desired_shipment_date == datetime(2032, 12, 1, 12, 35, 15, tzinfo=timezone.utc)

    assert placed.user.email == 'zaboy@gmail.com'
    assert placed.user.first_name == 'Забой'
    assert placed.user.last_name == 'Шахтёров'

    assert placed.giver.email == 'kamaz@gmail.com'
    assert placed.giver.first_name == 'Камаз'
    assert placed.giver.last_name == 'Помоев'


@pytest.mark.parametrize('required_field_name', [
    'receiver_name',
    'receiver_email',
    'giver_name',
    'giver_email',
    'desired_shipment_date',
])
def test_required_fields(api, required_field_name, default_gift_data):

    del default_gift_data[required_field_name]
    got = api.post('/api/v2/courses/ruloning-oboev/gift/', default_gift_data, format='multipart', expected_status_code=400)

    assert required_field_name in got


def test_gift_message(api, default_gift_data):
    default_gift_data['gift_message'] = 'Гори в аду!'
    api.post('/api/v2/courses/ruloning-oboev/gift/', default_gift_data, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.gift_message == 'Гори в аду!'


def test_desired_shipment_date_no_timezone_saves_with_default_timezone(api, default_gift_data):
    default_gift_data['desired_shipment_date'] = '2032-12-01 12:35:15'  # timezone is empty
    api.post('/api/v2/courses/ruloning-oboev/gift/', default_gift_data, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.desired_shipment_date == datetime(2032, 12, 1, 12, 35, 15, tzinfo=ZoneInfo(settings.TIME_ZONE))
