from functools import partial
import json
import pytest
from uuid import uuid4

from tinkoff.dolyame import Dolyame

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _credentials(settings):
    settings.DOLYAME_LOGIN = "root"
    settings.DOLYAME_PASSWORD = "l0ve"
    settings.DOLYAME_CERTIFICATE_PATH = "tinkoff/tests/.fixtures/testing.pem"


@pytest.fixture(autouse=True)
def _absolute_host(settings):
    settings.ABSOLUTE_HOST = "https://tst.hst"


@pytest.fixture
def dolyame(order):
    return Dolyame(order=order)


@pytest.fixture
def idempotency_key() -> str:
    return str(uuid4())


@pytest.fixture
def add_dolyame_response(httpx_mock, order, idempotency_key):
    return lambda url_suffix: partial(
        httpx_mock.add_response,
        method="POST",
        url=f"https://partner.dolyame.ru/v1/orders/{order.slug}/{url_suffix}",
        match_headers={
            "X-Correlation-ID": idempotency_key,
        },
        json={},
    )


@pytest.fixture
def retrieve_request_json(httpx_mock):
    return lambda: json.loads(httpx_mock.get_request().content)
