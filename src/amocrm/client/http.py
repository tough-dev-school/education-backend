from json import JSONDecodeError
from typing import Any
from urllib.parse import urljoin

import httpx
from httpx import Response
import httpx_cache
from httpx_cache.cache.redis import RedisCache

from django.conf import settings

from amocrm.exceptions import AmoCRMException
from amocrm.services.access_token_getter import AmoCRMTokenGetter


class AmoCRMClientException(AmoCRMException):
    """Raises when client cannot make successful request"""


class AmoCRMCacheControl(httpx_cache.CacheControl):
    def is_response_fresh(self, *, request: httpx.Request, response: httpx.Response) -> bool:
        """
        Override method to tell cache client to store Responses ignoring 'cache' headers
        https://obendidi.github.io/httpx-cache/cache_control/#use-your-own-cachecontroller
        """
        return True


class AmoCRMCacheControlTransport(httpx_cache.CacheControlTransport):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.controller = AmoCRMCacheControl(
            cacheable_methods=("GET",),
            cacheable_status_codes=(200, 203, 300, 301, 308),
            always_cache=True,
        )


def get_client(cached: bool = False) -> httpx.Client | httpx_cache.Client:
    cache_url = settings.HTTP_CACHE_REDIS_URL
    if cached:
        if len(cache_url) == 0:
            raise AmoCRMClientException("No cache url for client")
        cache = RedisCache(redis_url=cache_url)
        return httpx_cache.Client(
            transport=AmoCRMCacheControlTransport(cache=cache),
        )

    return httpx.Client()


def request(
    method: str,
    url: str,
    data: dict | list | None = None,
    params: dict | None = None,
    expected_status_codes: list[int] | None = None,
    cached: bool = False,
) -> dict[str, Any]:
    client = get_client(cached=cached)
    request = getattr(client, method)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {AmoCRMTokenGetter()()}",
    }
    url = format_url(url)

    if method in {"get", "delete"}:
        response = request(url=url, timeout=3, params=params, headers=headers)
    else:
        response = request(url=url, timeout=3, json=data, headers=headers)

    return get_validated_response(response=response, url=url, expected_status_codes=expected_status_codes)


def format_url(url: str) -> str:
    base_url = settings.AMOCRM_BASE_URL
    return urljoin(base_url, url.lstrip("/"))


def get_validated_response(response: Response, url: str, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
    try:
        response_json = response.json()
    except JSONDecodeError:
        response_json = {}

    expected_status_codes = expected_status_codes or [200]
    if response.status_code not in expected_status_codes:
        raise AmoCRMClientException(f"Non-ok HTTP response from amocrm: {response.status_code}\nResponse data: {response_json}")

    errors = response_json.get("_embedded", {}).get("errors") if isinstance(response_json, dict) else None
    if errors:
        raise AmoCRMClientException(f"Errors in response to {url}: {errors}")
    return response_json


def get(url: str, params: dict | None = None, expected_status_codes: list[int] | None = None, cached: bool = False) -> dict[str, Any]:
    return request(
        method="get",
        url=url,
        params=params,
        expected_status_codes=expected_status_codes,
        cached=cached,
    )


def delete(url: str, params: dict | None = None, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
    return request(
        method="delete",
        url=url,
        params=params,
        expected_status_codes=expected_status_codes,
    )


def post(url: str, data: dict | list, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
    return request(
        method="post",
        url=url,
        data=data,
        expected_status_codes=expected_status_codes,
    )


def patch(url: str, data: dict | list, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
    return request(
        method="patch",
        url=url,
        data=data,
        expected_status_codes=expected_status_codes,
    )


__all__ = [
    "get",
    "post",
    "delete",
    "patch",
]
