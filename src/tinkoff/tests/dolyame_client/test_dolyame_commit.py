from functools import partial
import pytest

from tinkoff import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def add_commit_response(add_dolyame_response):
    return partial(add_dolyame_response, url_suffix="commit")


def test_dolyame_commit_send_correct_request(order, add_commit_response, idempotency_key, retrieve_request_json, respx_mock):
    add_commit_response()

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)

    commit_request = retrieve_request_json()
    assert commit_request["amount"] == "100500"
    assert len(commit_request["items"]) == 1
    assert commit_request["fiscalization_settings"]["type"] == "enabled"
    assert commit_request["fiscalization_settings"]["params"]["create_receipt_for_committed_items"] is True
    assert commit_request["fiscalization_settings"]["params"]["create_receipt_for_added_items"] is True
    assert commit_request["fiscalization_settings"]["params"]["create_receipt_for_returned_items"] is True


def test_dolyame_commit_correct_per_items_data(order, add_commit_response, idempotency_key, retrieve_request_json):
    add_commit_response()

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)

    item_in_request = retrieve_request_json()["items"][0]
    assert item_in_request["name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert item_in_request["price"] == "100500"
    assert item_in_request["quantity"] == 1
    assert item_in_request["receipt"]["payment_method"] == "full_payment"
    assert item_in_request["receipt"]["tax"] == "none"
    assert item_in_request["receipt"]["payment_object"] == "service"
    assert item_in_request["receipt"]["measurement_unit"] == "шт"


@pytest.mark.xfail(strict=True, reason="Just to make sure above code works")
def test_header(order, idempotency_key, add_commit_response):
    add_commit_response(
        headers={
            "X-Correlation-ID": "SOME-OTHER-VALUE",
        }
    )

    tasks.commit_dolyame_order(order_id=order.id, idempotency_key=idempotency_key)
