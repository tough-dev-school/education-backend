from typing import Any
from urllib.parse import urljoin

import httpx

from django.conf import settings

from amocrm.services.access_token_getter import AmoCRMTokenGetter


class AmoCRMClientException(Exception):
    pass


class AmoCRMHTTP:
    def __init__(self) -> None:
        self.base_url = settings.AMOCRM_BASE_URL
        self.client = httpx.Client()

    def post(self, url: str, data: dict[str, Any], expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="post",
            url=url,
            data=data,
            expected_status_codes=expected_status_codes,
        )

    def patch(self, url: str, data: dict[str, Any], expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="patch",
            url=url,
            data=data,
            expected_status_codes=expected_status_codes,
        )

    def request(self, method: str, url: str, data: dict[str, Any] | None = None, expected_status_codes: list[int] | None = None) -> dict[str, Any]:
        request = getattr(self.client, method)
        response = request(
            url=self.format_url(url),
            timeout=3,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.access_token}",
            },
        )

        expected_status_codes = expected_status_codes or [200]
        if response.status_code not in expected_status_codes:
            raise AmoCRMClientException(f"Non-ok HTTP response from amocrm: {response.status_code}")

        response_json = response.json()

        errors = response_json.get("_embedded", {}).get("errors")
        if errors:
            raise AmoCRMClientException(f"Errors in response to {url}: {errors}")

        return response_json

    @property
    def access_token(self) -> str:
        return AmoCRMTokenGetter()()

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip("/"))
