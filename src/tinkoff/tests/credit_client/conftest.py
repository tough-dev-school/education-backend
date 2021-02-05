import pytest
import requests_mock

from tinkoff.credit import TinkoffCredit

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _tinkoff_credentials(settings):
    settings.TINKOFF_CREDIT_SHOP_ID = '1234'
    settings.TINKOFF_CREDIT_DEMO_MDOE = False


@pytest.fixture(autouse=True)
def _absolute_host(settings):
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
        client = TinkoffCredit(order)

        client.m = m

        yield client
