import pytest

import respx

from tinkoff.credit import TinkoffCredit

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _tinkoff_credentials(settings):
    settings.TINKOFF_CREDIT_SHOP_ID = "1234"
    settings.TINKOFF_CREDIT_SHOWCASE_ID = "123-45"
    settings.TINKOFF_CREDIT_DEMO_MDOE = False


@pytest.fixture(autouse=True)
def _absolute_host(settings):
    settings.ABSOLUTE_HOST = "https://tst.hst"
    settings.FRONTEND_URL = "https://front.tst.hst"


@pytest.fixture
def tinkoff(order):
    with respx.mock() as m:
        client = TinkoffCredit(order)

        client.m = m

        yield client
