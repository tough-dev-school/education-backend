from dataclasses import dataclass
from urllib.parse import urlencode
from urllib.parse import urljoin

import httpx

from apps.dashamail import exceptions


@dataclass
class DashamailFrontendHTTP:
    def post(self, url: str, user_agent: str, origin: str, payload: dict):
        response = httpx.post(
            url=self.format_url(url),
            text=self.format_payload(payload),
            headers={
                "user_agent": user_agent,
                "origin": origin,
                "referer": origin,
            },
        )

        response_json = self.get_json(response)
        if response.status_code != 200 or response_json is None:
            raise exceptions.DashamailWrongResponse(f"{response.status_code}: {response_json}")

    @property
    def base_url(self) -> str:
        return "https://directcrm.dashamail.com"

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip("&"))

    @staticmethod
    def format_payload(payload: dict) -> str:
        encoded = urlencode(payload)

        return encoded.replace("%27", "%22")
