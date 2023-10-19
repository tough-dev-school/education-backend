import pytest

from django.core.cache import cache

from apps.amocrm.client import http
from apps.amocrm.client.http import AmoCRMClientException

pytestmark = [
    pytest.mark.single_thread,
    pytest.mark.freeze_time("2023-09-08 11:17:12-04:00"),
]


@pytest.fixture(autouse=True)
def _cached_tokens():
    cache.set("amocrm_access_token", "token")
    cache.set("amocrm_refresh_token", "refresh-token")


@pytest.fixture
def amocrm_not_allowing_cache_headers():
    return {
        "cache-control": "no-store, no-cache, must-revalidate",
        "date": "Fri, 08 Sep 2023 11:17:12 GMT",
        "expires": "Tue, 15 Nov 1994 12:45:26 GMT",
        "pragma": "no-cache",
    }


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
def test_format_url(url, expected):
    assert http.format_url(url) == expected


@pytest.mark.parametrize(("method", "token"), [("post", "some-token"), ("patch", "another-token")])
def test_request_has_authorization_header(method, token, mocker):
    mock_request = mocker.patch(f"httpx.Client.{method}", return_value=MockResponse())
    cache.set("amocrm_access_token", token)
    request = getattr(http, method)

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


def test_get_ok(respx_mock):
    respx_mock.get(url="https://test.amocrm.ru/api/v4/companies?limit=100500").respond(json={"ok": True})

    got = http.get("api/v4/companies", params={"limit": 100500})

    assert "ok" in got


def test_get_ok_with_expected_status_code(respx_mock):
    respx_mock.get(url="https://test.amocrm.ru/api/v4/companies?limit=100500").respond(json={"ok": True}, status_code=321)
    got = http.get("api/v4/companies", expected_status_codes=[321], params={"limit": 100500})

    assert "ok" in got


def test_get_cached(respx_mock, amocrm_not_allowing_cache_headers):
    respx_mock.get("https://test.amocrm.ru/api/v4/companies?limit=100500").respond(
        200,
        json={"ok": "bar"},
        headers=amocrm_not_allowing_cache_headers,  # imitate real Amo response with not allowing cache headers
    )
    http.get("api/v4/companies", params={"limit": 100500}, cached=True)
    respx_mock.get("https://test.amocrm.ru/api/v4/companies?limit=100500").respond(500)  # throw 500 error

    got = http.get("api/v4/companies", params={"limit": 100500}, cached=True)

    assert "ok" in got  # client used cached value and didn't fail with 500


def test_delete_ok(respx_mock):
    respx_mock.delete(url="https://test.amocrm.ru/api/v4/transactions/444")

    got = http.delete("api/v4/transactions/444")

    assert got == {}


def test_delete_ok_with_expected_status_code(respx_mock):
    respx_mock.delete(url="https://test.amocrm.ru/api/v4/transactions/444").respond(status_code=321)

    got = http.delete("api/v4/transactions/444", expected_status_codes=[321])

    assert got == {}


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_ok(respx_mock, method):
    getattr(respx_mock, method)(url="https://test.amocrm.ru/api/v4/companies").respond(json={"ok": True})
    request = getattr(http, method)

    got = request("api/v4/companies", {})

    assert "ok" in got


@pytest.mark.parametrize("method", ["post", "patch"])
def test_ok_with_expected_status_code(respx_mock, method):
    getattr(respx_mock, method)(url="https://test.amocrm.ru/api/v4/companies").respond(json={"ok": True}, status_code=100500)
    request = getattr(http, method)

    got = request("api/v4/companies", {}, expected_status_codes=[100500])

    assert "ok" in got


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_fail(respx_mock, method):
    getattr(respx_mock, method)(url="https://test.amocrm.ru/api/v4/companies").respond(status_code=210)
    request = getattr(http, method)

    with pytest.raises(AmoCRMClientException, match="Non-ok HTTP response from apps.amocrm: 210"):
        request("api/v4/companies", {})


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_fail_with_body(respx_mock, method):
    getattr(respx_mock, method)(url="https://test.amocrm.ru/api/v4/companies").respond(status_code=210, json={"info": "damn we lost"})
    request = getattr(http, method)

    with pytest.raises(AmoCRMClientException, match="Non-ok HTTP response from apps.amocrm: 210\nResponse data: {'info': 'damn we lost'}"):
        request("api/v4/companies", {})


@pytest.mark.parametrize("method", ["post", "patch"])
def test_request_fail_because_of_errors_in_response(respx_mock, method):
    getattr(respx_mock, method)(url="https://test.amocrm.ru/api/v4/companies").respond(json={"_embedded": {"errors": [["All my life is an error"]]}})
    request = getattr(http, method)

    with pytest.raises(AmoCRMClientException, match="Errors in response to https://test.amocrm.ru/api/v4/companies:"):
        request("api/v4/companies", {})
