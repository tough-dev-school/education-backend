from decimal import Decimal

import pytest

from orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def record(mixer):
    return mixer.blend('courses.Record', slug='home-video')


@pytest.fixture(autouse=True)
def payment_url(mocker):
    return mocker.patch('tinkoff.client.TinkoffBank.get_initial_payment_url', return_value='https://bank.test/pay/')


def get_order():
    return Order.objects.last()


def test_order(client, record):
    client.post('/api/v2/records/home-video/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'price': 1900,
    })

    placed = get_order()

    assert placed.item == record
    assert placed.price == Decimal('1900.00')


def test_user(client, record):
    client.post('/api/v2/records/home-video/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'price': 1900,
    })

    placed = get_order()

    assert placed.user.first_name == 'Забой'
    assert placed.user.last_name == 'Шахтёров'
    assert placed.user.email == 'zaboy@gmail.com'


def test_redirect(client, record):
    response = client.post('/api/v2/records/home-video/purchase/', {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
        'price': 1900,
    })

    assert response.status_code == 302
    assert response['Location'] == 'https://bank.test/pay/'


def test_invalid(client):
    response = client.post('/api/v2/records/home-video/purchase/', {})

    assert response.status_code == 400
