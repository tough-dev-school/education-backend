import pytest

from app.integrations.dashamail.exceptions import DashamailWrongResponse

pytestmark = [pytest.mark.django_db]


def test_post_ok(dashamail, successful_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com", method="POST", json=successful_response_json)

    assert dashamail.http.post("", payload={}) == successful_response_json


def test_post_no_content(dashamail):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com/test/", method="POST")

    with pytest.raises(DashamailWrongResponse):
        assert dashamail.http.post("test/", payload={})


def test_post_wrong_status_code(dashamail, successful_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com/test/", method="POST", json=successful_response_json, status_code=500)

    with pytest.raises(DashamailWrongResponse):
        dashamail.http.post("test/", payload={})


def test_post_payload(dashamail, successful_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com/test/", method="POST", json=successful_response_json)

    dashamail.http.post(
        "test/",
        payload={
            "test": "test",
        },
    )

    assert b"test=test" in dashamail.httpx_mock.get_request().content


def test_api_key_in_payload(dashamail, successful_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com/test/", method="POST", json=successful_response_json)

    dashamail.http.post("test/", payload={})

    assert b"api_key=apikey" in dashamail.httpx_mock.get_request().content


def test_list_id_in_payload(dashamail, successful_response_json):
    dashamail.httpx_mock.add_response(url="https://api.dashamail.com/test/", method="POST", json=successful_response_json)

    dashamail.http.post("test/", payload={})

    assert b"list_id=1" in dashamail.httpx_mock.get_request().content
