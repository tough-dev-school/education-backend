from uuid import uuid4

import pytest
from respx import MockRouter

from apps.tinkoff import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def idempotency_key() -> str:
    return str(uuid4())


@pytest.fixture
def add_refund_response(order, idempotency_key, respx_mock: MockRouter):
    def add_response(headers: dict | None = None):
        return respx_mock.post(
            url__eq=f"https://partner.dolyame.ru/v1/orders/{order.slug}/refund",
            headers=headers or {"X-Correlation-ID": idempotency_key},
        ).respond(json={})

    return add_response


def test_send_correct_refund_request(order, idempotency_key, add_refund_response, retrieve_request_json):
    add_refund_response()

    tasks.refund_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)

    refund_request = retrieve_request_json()
    assert refund_request["amount"] == "100500"
    assert refund_request["fiscalization_settings"] == {"type": "enabled"}
    assert len(refund_request["returned_items"]) == 1


def test_send_correct_refund_request_per_items_data(order, idempotency_key, add_refund_response, retrieve_request_json):
    add_refund_response()

    tasks.refund_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)

    refunded_item_in_request = retrieve_request_json()["returned_items"][0]
    assert refunded_item_in_request["name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert refunded_item_in_request["price"] == "100500"
    assert refunded_item_in_request["quantity"] == 1
    assert refunded_item_in_request["receipt"]["payment_method"] == "full_payment"
    assert refunded_item_in_request["receipt"]["tax"] == "none"
    assert refunded_item_in_request["receipt"]["payment_object"] == "service"
    assert refunded_item_in_request["receipt"]["measurement_unit"] == "шт"


@pytest.mark.xfail(strict=True, reason="Just to make sure above code works")
def test_header(order, idempotency_key, add_refund_response):
    add_refund_response(
        match_headers={
            "X-Correlation-ID": "SOME-OTHER-VALUE",
        }
    )

    tasks.refund_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)
