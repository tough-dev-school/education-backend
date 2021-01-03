import pytest
import requests_mock

from tinkoff.client import TinkoffBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = 'k3y'
    settings.TINKOFF_TERMINAL_PASSWORD = '123456'


@pytest.fixture(autouse=True)
def absolute_host(settings):
    settings.ABSOLUTE_HOST = 'https://tst.hst'
    settings.FRONTEND_URL = 'https://front.tst.hst'


@pytest.fixture
def record(mixer):
    return mixer.blend(
        'products.Record',
        name='Пентакли и тентакли',
        name_receipt='Предоставление доступа к записи курса «Пентакли и Тентакли»',
    )


@pytest.fixture
def order(mixer, record):
    return mixer.blend('orders.Order', record=record, price='100.50')


@pytest.fixture
def tinkoff(user, order):
    with requests_mock.Mocker() as m:
        client = TinkoffBank(order)

        client.m = m

        yield client
