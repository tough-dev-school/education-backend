import pytest
import uuid
from pytest_httpx import HTTPXMock

from tinkoff import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def idempotency_key() -> str:
    return str(uuid.uuid4())


def test(order, idempotency_key, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=f'https://partner.dolyame.ru/v1/orders/tds-{order.id}/commit',
        match_headers={
            'X-Correlation-ID': idempotency_key,
        },
        json={},
    )

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)


@pytest.mark.xfail(strict=True, reason='Just to make sure above code works')
def test_header(order, idempotency_key, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url=f'https://partner.dolyame.ru/v1/orders/tds-{order.id}/commit',
        match_headers={
            'X-Correlation-ID': 'SOME-OTHER-VALUE',
        },
        json={},
    )

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)
