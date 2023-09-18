import pytest

from respx import MockRouter

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def add_create_response(respx_mock: MockRouter):
    return respx_mock.post(
        url__eq="https://partner.dolyame.ru/v1/orders/create",
    ).respond(json={"link": "__mocked"})


def test_order_data(dolyame, order, retrieve_request_json):
    dolyame.get_initial_payment_url()

    create_request = retrieve_request_json()
    assert create_request["order"]["id"] == order.slug
    assert create_request["order"]["amount"] == "100500"
    assert create_request["order"]["items"][0]["name"] == "Предоставление доступа к записи курса «Пентакли и Тентакли»"
    assert create_request["order"]["items"][0]["quantity"] == 1
    assert create_request["order"]["items"][0]["price"] == "100500"
    assert create_request["client_info"]["first_name"] == "Авраам Соломонович"
    assert create_request["client_info"]["last_name"] == "Пейзенгольц"
    assert create_request["client_info"]["email"] == "avraam-the-god@gmail.com"
    assert create_request["fiscalization_settings"]["type"] == "enabled"


def test_return_value(dolyame):
    url = dolyame.get_initial_payment_url()

    assert url == "__mocked"


def test_random_idempotency_key_inserted_in_headers(dolyame, respx_mock):
    dolyame.get_initial_payment_url()

    create_request_headers = respx_mock.calls.last.request.headers
    assert "X-Correlation-ID" in create_request_headers
    assert "-4" in create_request_headers["X-Correlation-ID"], "Should be randum UUID4"
