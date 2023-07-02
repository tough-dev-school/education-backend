from datetime import datetime
from urllib.parse import urljoin

import jwt
import requests

from django.utils.functional import cached_property

TIMEOUT = 10


class ZoomusHTTPException(Exception):
    pass


class ZoomusClientHTTP:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://api.zoom.us/"):
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret

    @cached_property
    def token(self) -> str:
        return jwt.encode(
            payload={
                "iss": self.api_key,
                "exp": datetime.utcnow().timestamp() + 3600 * 5,
            },
            key=self.api_secret,
            algorithm="HS256",
        )

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip("/"))

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
        }

    def post(self, url: str, data: dict, expected_status_code: int = 200) -> dict:
        response = requests.post(
            self.format_url(url),
            timeout=TIMEOUT,
            json=data,
            headers=self.headers,
        )

        json = response.json()
        if response.status_code != expected_status_code:
            if "message" in json:
                msg = f'Error from zoom.us: {json["message"]}, errors: {json.get("errors")}'
            else:
                msg = f"Non-ok HTTP response from zoom.us: {response.status_code}"

            raise ZoomusHTTPException(msg)

        return json

    def get(self, url: str) -> dict:
        response = requests.get(
            self.format_url(url),
            timeout=TIMEOUT,
            headers=self.headers,
        )
        if response.status_code != 200:
            raise ZoomusHTTPException(f"Non-ok HTTP response from zoom.us: {response.status_code}")

        return response.json()
