import pytest
from decimal import Decimal

from orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures('bundle'),
]


def get_order():
    return Order.objects.last()


def test_order(api, bundle, default_user_data):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.item == bundle
    assert placed.price == Decimal('1900.00')


def test_user(api, bundle, default_user_data):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.user.first_name == 'Забой'
    assert placed.user.last_name == 'Шахтёров'
    assert placed.user.email == 'zaboy@gmail.com'


@pytest.mark.parametrize('wants_to_subscribe', [True, False])
def test_user_auto_subscription(api, wants_to_subscribe, default_user_data):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
        'subscribe': wants_to_subscribe,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.user.subscribed is wants_to_subscribe


def test_subscription_tags(api, bundle, subscribe, default_user_data):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
        'subscribe': True,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    subscribe.assert_called_once_with(user_id=placed.user.pk, tags=['pinetree-tickets'])


def test_by_default_user_is_not_subscribed(api, default_user_data):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
    }, format='multipart', expected_status_code=302)

    placed = get_order()

    assert placed.user.subscribed is False


def test_redirect(api, bundle, default_user_data):
    response = api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
    }, format='multipart', expected_status_code=302, as_response=True)

    assert response.status_code == 302
    assert response['Location'] == 'https://bank.test/pay/'


def test_custom_success_url(api, bundle, bank, default_user_data):
    api.post('/api/v2/bundles/pinetree-tickets/purchase/', {
        **default_user_data,
        'success_url': 'https://ok.true/yes',
    }, format='multipart', expected_status_code=302)

    assert bank.call_args[1]['success_url'] == 'https://ok.true/yes'


def test_invalid(client):
    response = client.post('/api/v2/bundles/pinetree-tickets/purchase/', {})

    assert response.status_code == 400
