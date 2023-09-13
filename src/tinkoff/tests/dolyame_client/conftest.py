import json
import pytest
from uuid import uuid4

from respx import MockRouter

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
def add_dolyame_response(order, idempotency_key, respx_mock: MockRouter):
    def add_response(url_suffix: str, headers: dict | None = None):
        return respx_mock.post(
            url__eq=f"https://partner.dolyame.ru/v1/orders/{order.slug}/{url_suffix}",
            headers=headers or {"X-Correlation-ID": idempotency_key},
        ).respond(json={})

    return add_response


@pytest.fixture
def retrieve_request_json(respx_mock: MockRouter):
    return lambda: json.loads(respx_mock.calls.last.request.content)
