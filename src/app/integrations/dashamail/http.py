from urllib.parse import urljoin

import httpx

from django.conf import settings

from app.integrations.dashamail import exceptions


class DashamailHTTP:
    @property
    def base_url(self) -> str:
        return "https://api.dashamail.com"

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip("&"))

    def request(self, url: str, *, method: str, payload: dict | None = None) -> dict:
        if payload is None:
            payload = {}

        payload["api_key"] = settings.DASHAMAIL_API_KEY

        response = httpx.request(
            method=method,
            url=self.format_url(url),
            data=payload,
        )

        response_json = self.get_json(response)
        if response.status_code != 200 or response_json is None:
            raise exceptions.DashamailWrongResponse(f"{response.status_code}: {response_json}")

        return response_json

    def post(self, url: str, payload: dict) -> dict:
        return self.request(url, method="POST", payload=payload)

    @staticmethod
    def get_json(response: httpx.Response) -> dict | None:
        if response.text:
            return response.json()
