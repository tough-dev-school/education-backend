import pytest
import respx

from apps.tinkoff.bank import TinkoffBank

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = "k3y"
    settings.TINKOFF_TERMINAL_PASSWORD = "123456"


@pytest.fixture(autouse=True)
def _set_absolute_host(settings):
    settings.ABSOLUTE_HOST = "https://tst.hst"
    settings.FRONTEND_URL = "https://front.tst.hst"


@pytest.fixture
def tinkoff(user, order):  # noqa: ARG001
    with respx.mock() as m:
        client = TinkoffBank(order)

        client.m = m

        yield client
