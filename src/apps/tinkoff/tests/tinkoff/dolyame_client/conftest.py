import pytest

from apps.tinkoff.dolyame import Dolyame

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _credentials(settings):
    settings.DOLYAME_LOGIN = "root"
    settings.DOLYAME_PASSWORD = "l0ve"
    settings.DOLYAME_CERTIFICATE_PATH = "apps/tinkoff/tests/tinkoff/.fixtures/testing.pem"


@pytest.fixture(autouse=True)
def _absolute_host(settings):
    settings.ABSOLUTE_HOST = "https://tst.hst"


@pytest.fixture
def dolyame(order):
    return Dolyame(order=order)
