import pytest

from django.core.cache import cache

from amocrm.client import AmoCRMClientException

pytestmark = [
    pytest.mark.single_thread,
]


class MockResponse:
    status_code = 200

    def json(self) -> dict:
        return {}


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("/test/create", "https://test.amocrm.ru/test/create"),
        ("test/create", "https://test.amocrm.ru/test/create"),
        ("test/create/?par=val", "https://test.amocrm.ru/test/create/?par=val"),
        (
            "test/create/?par=val&par1=val1",
            "https://test.amocrm.ru/test/create/?par=val&par1=val1",
        ),
    ],
)
def test_format_url(url, expected, amocrm_client):
    assert amocrm_client.format_url(url) == expected


@pytest.mark.parametrize(("method", "token"), [("post", "some-token"), ("patch", "another-token")])
def test_request_has_authorization_header(amocrm_client, method, token, mocker):
    mock_request = mocker.patch(f"httpx.Client.{method}", return_value=MockResponse())
    cache.set("amocrm_access_token", token)
    request = getattr(amocrm_client, method)

    request("api/v4/companies", {})

    mock_request.assert_called_once_with(
        url="https://test.amocrm.ru/api/v4/companies",
        timeout=3,
        json={},
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )


def test_get_ok(amocrm_client, httpx_mock):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/companies?limit=100500", method="GET", json={"ok": True})

    got = amocrm_client.get("api/v4/companies", params={"limit": 100500})

    assert "ok" in got


def test_get_ok_with_expected_status_code(amocrm_client, httpx_mock):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/companies?limit=100500", method="GET", json={"ok": True}, status_code=321)
    got = amocrm_client.get("api/v4/companies", expected_status_codes=[321], params={"limit": 100500})

    assert "ok" in got


def test_get_cached(amocrm_client, respx_mock):
    respx_mock.get("https://test.amocrm.ru/api/v4/companies?limit=100500").respond(200, json={"ok": "bar"})
    amocrm_client.get("api/v4/companies", params={"limit": 100500}, cached=True)
    respx_mock.get("https://test.amocrm.ru/api/v4/companies?limit=100500").respond(200, json={"foo": "bar"})

    got = amocrm_client.get("api/v4/companies", params={"limit": 100500}, cached=True)

    assert "ok" in got


def test_get_default_not_cached(amocrm_client, respx_mock):
    respx_mock.get("https://test.amocrm.ru/api/v4/companies?limit=100500").respond(200, json={"ok": "bar"})
    amocrm_client.get("api/v4/companies", params={"limit": 100500})
    respx_mock.get("https://test.amocrm.ru/api/v4/companies?limit=100500").respond(200, json={"foo": "bar"})

    got = amocrm_client.get("api/v4/companies", params={"limit": 100500})

    assert "foo" in got


def test_delete_ok(amocrm_client, httpx_mock):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/transactions/444", method="DELETE")

    got = amocrm_client.delete("api/v4/transactions/444")

    assert got == {}


def test_delete_ok_with_expected_status_code(amocrm_client, httpx_mock):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/transactions/444", method="DELETE", status_code=321)

    got = amocrm_client.delete("api/v4/transactions/444", expected_status_codes=[321])

    assert got == {}


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_ok(amocrm_client, httpx_mock, method):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/companies", method=method, json={"ok": True})
    request = getattr(amocrm_client, method)

    got = request("api/v4/companies", {})

    assert "ok" in got


@pytest.mark.parametrize("method", ["post", "patch"])
def test_ok_with_expected_status_code(amocrm_client, httpx_mock, method):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/companies", json={"ok": True}, method=method, status_code=100500)
    request = getattr(amocrm_client, method)

    got = request("api/v4/companies", {}, expected_status_codes=[100500])

    assert "ok" in got


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_fail(amocrm_client, httpx_mock, method):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/companies", method=method, status_code=210)
    request = getattr(amocrm_client, method)

    with pytest.raises(AmoCRMClientException, match="Non-ok HTTP response from amocrm: 210"):
        request("api/v4/companies", {})


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_fail_with_body(amocrm_client, httpx_mock, method):
    httpx_mock.add_response(url="https://test.amocrm.ru/api/v4/companies", method=method, status_code=210, json={"info": "damn we lost"})
    request = getattr(amocrm_client, method)

    with pytest.raises(AmoCRMClientException, match="Non-ok HTTP response from amocrm: 210\nResponse data: {'info': 'damn we lost'}"):
        request("api/v4/companies", {})


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_fail_because_of_errors_in_response(amocrm_client, httpx_mock, method):
    httpx_mock.add_response(
        url="https://test.amocrm.ru/api/v4/companies",
        method=method,
        json={"_embedded": {"errors": [["All my life is an error"]]}},
    )
    request = getattr(amocrm_client, method)

    with pytest.raises(AmoCRMClientException, match="Errors in response to https://test.amocrm.ru/api/v4/companies:"):
        request("api/v4/companies", {})
