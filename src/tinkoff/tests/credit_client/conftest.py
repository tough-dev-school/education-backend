import pytest
import requests_mock

from tinkoff.credit import TinkoffCredit

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _tinkoff_credentials(settings):
    settings.TINKOFF_CREDIT_SHOP_ID = '1234'
    settings.TINKOFF_CREDIT_SHOWCASE_ID = '123-45'
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
def order(mixer, user, record):
    return mixer.blend('orders.Order', user=user, record=record, price='100500')


@pytest.fixture
def tinkoff(order):
    with requests_mock.Mocker() as m:
        client = TinkoffCredit(order)

        client.m = m

        yield client


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Авраам Соломонович', last_name='Пейзенгольц')
