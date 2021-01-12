from typing import Optional

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin


class MailchimpHTTPException(BaseException):
    pass


class MailchimpWrongResponse(MailchimpHTTPException):
    pass


class MailchimpNotFound(MailchimpHTTPException):
    pass


class MailchimpHTTP:
    @property
    def base_url(self) -> str:
        dc = settings.MAILCHIMP_API_KEY.split('-')[-1]

        return f'https://{dc}.api.mailchimp.com/3.0/'

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip('/'))

    def request(self, url, method, payload: Optional[dict] = None, expected_status_code: int = 200):
        requests_payload = dict()
        if payload is not None:
            requests_payload['json'] = payload

        response = requests.request(
            method=method,
            url=self.format_url(url),
            auth=HTTPBasicAuth('user', settings.MAILCHIMP_API_KEY),
            **requests_payload,
        )

        if response.status_code == 404:
            raise MailchimpNotFound()

        if response.status_code != expected_status_code:
            raise MailchimpWrongResponse(f'{response.status_code}: {self.get_json(response)}')

        return self.get_json(response)

    def get(self, url: str, *args, **kwargs):
        return self.request(url, method='GET', *args, **kwargs)

    def post(self, url: str, payload: dict, *args, **kwargs):
        return self.request(url, method='POST', payload=payload, *args, **kwargs)

    @staticmethod
    def get_json(response):
        if len(response.text):
            return response.json()
