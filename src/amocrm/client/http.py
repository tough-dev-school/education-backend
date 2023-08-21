from json import JSONDecodeError
from typing import Any
from urllib.parse import urljoin

import httpx
from httpx import Response

from django.conf import settings

from amocrm.exceptions import AmoCRMException
from amocrm.services.access_token_getter import AmoCRMTokenGetter


class AmoCRMClientException(AmoCRMException):
    """Raises when client cannot make successful request"""


class AmoCRMHTTP:
    def __init__(self) -> None:
        self.base_url = settings.AMOCRM_BASE_URL
        self.client = httpx.Client()

    def get(self, url: str, params: dict | None = None, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="get",
            url=url,
            params=params,
            expected_status_codes=expected_status_codes,
        )

    def delete(self, url: str, params: dict | None = None, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="delete",
            url=url,
            params=params,
            expected_status_codes=expected_status_codes,
        )

    def post(self, url: str, data: dict | list, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="post",
            url=url,
            data=data,
            expected_status_codes=expected_status_codes,
        )

    def patch(self, url: str, data: dict | list, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="patch",
            url=url,
            data=data,
            expected_status_codes=expected_status_codes,
        )

    def request(
        self, method: str, url: str, data: dict | list | None = None, params: dict | None = None, expected_status_codes: list[int] | None = None
    ) -> dict[str, Any]:
        request = getattr(self.client, method)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        url = self.format_url(url)

        if method in {"get", "delete"}:
            response = request(url=url, timeout=3, params=params, headers=headers)
        else:
            response = request(url=url, timeout=3, json=data, headers=headers)

        return self.get_validated_response(response=response, url=url, expected_status_codes=expected_status_codes)

    @property
    def access_token(self) -> str:
        return AmoCRMTokenGetter()()

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip("/"))

    @staticmethod
    def get_validated_response(response: Response, url: str, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        expected_status_codes = expected_status_codes or [200]
        if response.status_code not in expected_status_codes:
            try:
                response_json = response.json()
                raise AmoCRMClientException(f"Non-ok HTTP response from amocrm: {response.status_code}\nResponse data: {response_json}")
            except JSONDecodeError:
                raise AmoCRMClientException(f"Non-ok HTTP response from amocrm: {response.status_code}")

        try:
            response_json = response.json()

            errors = response_json.get("_embedded", {}).get("errors") if isinstance(response_json, dict) else None
            if errors:
                raise AmoCRMClientException(f"Errors in response to {url}: {errors}")

            return response_json
        except JSONDecodeError:
            return {}
