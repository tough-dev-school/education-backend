from typing import Any

import httpx
import json
from django.conf import settings
from django.utils.functional import cached_property
from urllib.parse import urljoin

from tinkoff.business_client.exceptions import TinkoffBusinessHTTPException

SimpleJSONType = list[dict[str, Any]] | dict[str, Any]


class TinkoffBusinessHTTP:
    @cached_property
    def base_url(self) -> str:
        if settings.TINKOFF_BUSINESS_DEMO_MODE:
            return 'https://business.tinkoff.ru/openapi/sandbox/api/v1/'
        return 'https://business.tinkoff.ru/openapi/api/v1/'

    @cached_property
    def token(self) -> str:
        if settings.TINKOFF_BUSINESS_DEMO_MODE:
            return 'TinkoffOpenApiSandboxSecretToken'
        return settings.TINKOFF_BUSINESS_TOKEN

    @cached_property
    def headers(self) -> dict[str, str]:
        return {
            'Authorization': f'Bearer {self.token}',
        }

    def request(
        self,
        url: str,
        *,
        method: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        expected_status_code: int = 200,
    ) -> SimpleJSONType:
        response = httpx.request(
            method=method,
            url=self.format_url(url),
            headers=self.headers,
            json=payload,
            params=params,
        )

        response_json = self.get_response_json(response)
        self.raise_if_error_occurs(response, response_json, expected_status_code)
        return response_json

    def get(self, url: str, params: dict[str, Any] | None = None, expected_status_code: int = 200) -> SimpleJSONType:
        return self.request(url, method='GET', params=params, expected_status_code=expected_status_code)

    def post(self, url: str, payload: dict[str, Any] | None = None, expected_status_code: int = 201) -> SimpleJSONType:
        return self.request(url, method='POST', payload=payload, expected_status_code=expected_status_code)

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.strip('/'))

    def get_response_json(self, response: httpx.Response) -> Any:
        try:
            return response.json()
        except json.JSONDecodeError as decode_error:
            return {  # we save JSON decode errors in the same format as we receive from API
                'errorCode': 'RESPONSE_NOT_A_JSON',
                'errorMessage': f'Response not a valid JSON: {decode_error}',
            }

    def raise_if_error_occurs(self, response: httpx.Response, response_json: Any, expected_status_code: int) -> None:
        if 'errorCode' in response_json:
            raise TinkoffBusinessHTTPException(f"{response.status_code}: {response_json['errorMessage']}")
        if response.status_code != expected_status_code:
            raise TinkoffBusinessHTTPException(f'Non-expected HTTP response from tinkoff: {response.status_code}')
