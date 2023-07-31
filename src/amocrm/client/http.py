from typing import Any
from urllib.parse import urljoin

import httpx

from django.conf import settings

from amocrm.services.token_manager import AmoCRMTokenManager


class AmoCRMClientException(Exception):
    pass


class AmoCRMHTTP:
    base_url = settings.AMOCRM_BASE_URL
    client = httpx.Client()

    def post(self, url: str, data: dict[str, Any], expected_status_code: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="post",
            url=url,
            data=data,
            expected_status_code=expected_status_code,
        )

    def patch(self, url: str, data: dict[str, Any], expected_status_code: list[int] | None = None) -> dict[str, Any]:
        return self.request(
            method="patch",
            url=url,
            data=data,
            expected_status_code=expected_status_code,
        )

    @classmethod
    def format_url(cls, url: str) -> str:
        return urljoin(cls.base_url, url.lstrip("/"))

    @classmethod
    def request(cls, method: str, url: str, data: dict[str, Any] | None = None, expected_status_code: list[int] | None = None) -> dict[str, Any]:
        request = getattr(cls.client, method)
        response = request(
            url=cls.format_url(url),
            timeout=3,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {AmoCRMTokenManager()()}",
            },
        )

        expected_status_codes = expected_status_code or [200]
        if response.status_code not in expected_status_codes:
            raise AmoCRMClientException(f"Non-ok HTTP response from amocrm: {response.status_code}")

        response_json = response.json()

        errors = response_json.get("_embedded", {}).get("errors")
        if errors:
            raise AmoCRMClientException(f"Errors in response to {url}: {errors}")

        return response_json
