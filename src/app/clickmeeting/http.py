from typing import Dict, List, Union
from urllib.parse import urljoin

import requests

TIMEOUT = 10


class ClickMeetingHTTPException(Exception):
    pass


class ClickMeetingClientHTTP:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip('/'))

    @property
    def headers(self):
        return {
            'X-Api-Key': self.api_key,
        }

    def post(self, url: str, data: dict, expected_status_code: list = None) -> Union[List, Dict]:
        response = requests.post(
            self.format_url(url),
            timeout=TIMEOUT,
            data=data,
            headers=self.headers,
        )

        json = response.json()
        if response.status_code != 200:
            if 'errors' in json:
                msg = f'Error from ClickMeeting: {json["errors"]}'
            else:
                msg = f'Non-ok HTTP response from ClickMeeting: {response.status_code}'

            raise ClickMeetingHTTPException(msg)

        return json

    def get(self, url):
        response = requests.get(
            self.format_url(url),
            timeout=TIMEOUT,
            headers=self.headers,
        )
        if response.status_code != 200:
            raise ClickMeetingHTTPException(f"Non-ok HTTP response from ClickMeeting: {response.status_code}")

        return response.json()
