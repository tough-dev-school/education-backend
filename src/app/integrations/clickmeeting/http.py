from typing import Dict, List, Union
from urllib.parse import quote, urljoin

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
            'Content-Type': 'application/x-www-form-urlencoded',
        }

    def post(self, url: str, data: dict) -> Union[List, Dict]:
        response = requests.post(
            self.format_url(url),
            timeout=TIMEOUT,
            data=self.build_query(data),
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

    def build_query(self, data):
        """This shit is copy-pasted from https://github.com/ClickMeeting/DevZone/blob/master/API/examples/Python"""
        def build_query_item(params, base_key=None):
            results = list()

            if(type(params).__name__ == 'dict'):
                for key, value in params.items():
                    if(base_key):
                        new_base = quote("%s[%s]" % (base_key, key))
                        results += build_query_item(value, new_base)
                    else:
                        results += build_query_item(value, key)
            elif(type(params).__name__ == 'list'):
                for value in params:
                    if(base_key):
                        results += build_query_item(value, "%s[]" % (base_key))
                    else:
                        results += build_query_item(value)
            else:
                quoted_item = quote(params)
                if(base_key):
                    results.append("%s=%s" % (base_key, quoted_item))
                else:
                    results.append(quoted_item)
            return results

        return '&'.join(build_query_item(data))
