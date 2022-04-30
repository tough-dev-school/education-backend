import pytest

from tinkoff.dolyame import Dolyame

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _credentials(settings):
    settings.DOLYAME_LOGIN = 'root'
    settings.DOLYAME_PASSWORD = 'l0ve'
    settings.DOLYAME_CERTIFICATE_PATH = 'tinkoff/tests/.fixtures/testing.pem'


@pytest.fixture(autouse=True)
def _absolute_host(settings):
    settings.ABSOLUTE_HOST = 'https://tst.hst'


@pytest.fixture
def record(mixer):
    return mixer.blend(
        'products.Record',
        name='Пентакли и тентакли',
        name_receipt='Предоставление доступа к записи курса «Пентакли и Тентакли»',
    )


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Авраам Соломонович', last_name='Пейзенгольц')


@pytest.fixture
def order(factory, user, record):
    return factory.order(user=user, item=record, price='100500')


@pytest.fixture
def dolyame(order):
    return Dolyame(order=order)
