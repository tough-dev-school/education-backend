import pytest
import requests_mock

from tinkoff.bank import TinkoffBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = 'k3y'
    settings.TINKOFF_TERMINAL_PASSWORD = '123456'


@pytest.fixture
def record(mixer):
    return mixer.blend('courses.Record', name='Пентакли и тентакли')


@pytest.fixture
def order(mixer, record):
    return mixer.blend('orders.Order', record=record)


@pytest.fixture
def tinkoff(user, order):
    with requests_mock.Mocker() as m:
        client = TinkoffBank(order)

        client.m = m

        yield client
