import pytest

from tinkoff.bank import TinkoffBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle', slug='pinetree-tickets', name='Флаг и билет на ёлку', price=1900)


@pytest.fixture(autouse=True)
def payment_url(mocker):
    return mocker.patch.object(TinkoffBank, 'get_initial_payment_url', return_value='https://bank.test/pay/')


@pytest.fixture
def bank(mocker):
    class FakeBank:
        @classmethod
        def get_initial_payment_url(self):
            return 'https://bank.test/pay/'

    return mocker.patch.object(TinkoffBank, '__init__', return_value=None)


@pytest.fixture
def call_purchase(api, default_user_data):
    return lambda **kwargs: api.post(
        '/api/v2/bundles/pinetree-tickets/purchase/',
        {
            **default_user_data,
            **kwargs,
        },
        format='multipart', expected_status_code=302,
    )
