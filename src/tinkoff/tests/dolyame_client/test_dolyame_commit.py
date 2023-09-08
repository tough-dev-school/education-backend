import json
import pytest
import uuid

from tinkoff import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def idempotency_key() -> str:
    return str(uuid.uuid4())


def test(order, idempotency_key, respx_mock):
    respx_mock.route(
        url=f"https://partner.dolyame.ru/v1/orders/{order.slug}/commit",
        headers={
            "X-Correlation-ID": idempotency_key,
        },
    ).respond(json={})

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)
    result = json.loads(respx_mock.calls.last.request.content)

    assert result["amount"] == "100500"
    assert result["items"][0]["name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert result["items"][0]["price"] == "100500"
    assert result["items"][0]["quantity"] == 1


@pytest.mark.xfail(strict=True, reason="Just to make sure above code works")
def test_header(order, idempotency_key, respx_mock):
    respx_mock.route(
        url=f"https://partner.dolyame.ru/v1/orders/{order.slug}/commit",
        headers={
            "X-Correlation-ID": "SOME-OTHER-VALUE",
        },
    ).respond(json={})

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)
