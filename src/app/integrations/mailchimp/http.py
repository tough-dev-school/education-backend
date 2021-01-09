from typing import Optional

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin


class MailchimpHTTPException(BaseException):
    pass


class MailChimpWrongResponse(MailchimpHTTPException):
    pass


class MailChimpNotFound(MailchimpHTTPException):
    pass


class MailchimpHTTP:
    @property
    def base_url(self) -> str:
        dc = settings.MAILCHIMP_API_KEY.split('-')[-1]

        return f'https://{dc}.api.mailchimp.com/3.0/'

    def format_url(self, url: str) -> str:
        return urljoin(self.base_url, url.lstrip('/'))

    def request(self, url, method, payload: Optional[dict] = None):
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
            raise MailChimpNotFound()

        if response.status_code != 200:
            raise MailChimpWrongResponse(f'{response.status_code}: {response.json()}')

        return response

    def get(self, url: str):
        response = self.request(url, method='GET')

        return response.json()

    def post(self, url: str, payload: dict):
        response = self.request(url, method='POST', payload=payload)

        return response.json()
