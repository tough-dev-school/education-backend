import pytest

import httpx

from amocrm.client.http import AmoCRMCacheControl

pytestmark = [
    pytest.mark.freeze_time("2023-09-08 11:17:12-04:00"),
]


@pytest.fixture(scope="session")
def httpx_request():
    return httpx.Request("GET", "http://httpx-cache")


def test_response_fresh_no_headers(httpx_request):
    response = httpx.Response(200, content=b"httpx-cache-is-awesome")

    assert AmoCRMCacheControl().is_response_fresh(request=httpx_request, response=response) is True


@pytest.mark.parametrize(
    "headers",
    [
        {"expires": "Tue, 15 Nov 1994 12:45:26 GMT"},
        {"date": "Fri, 8 Sep 2023 12:45:26 GMT", "expires": "lala"},
        {"date": "Fri, 8 Sep 2023 12:45:26 GMT", "expires": "Tue, 15 Nov 1994 12:45:26 GMT"},
        {"date": "Fri, 8 Sep 2023 12:45:26 GMT", "expires": "Tue, 15 Nov 1994 12:45:26 GMT", "cache-control": "max-age=900"},
        {"date": "Fri, 8 Sep 2023 12:45:26 GMT", "expires": "Tue, 15 Nov 1994 12:45:26 GMT", "cache-control": "max-age=0"},
    ],
)
def test_is_response_fresh_with_any_cache_related_headers(headers, httpx_request):
    response = httpx.Response(200, headers=headers, content=b"httpx-cache-is-awesome")

    assert AmoCRMCacheControl().is_response_fresh(request=httpx_request, response=response) is True
