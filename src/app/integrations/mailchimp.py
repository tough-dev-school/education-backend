from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from users.models import User


class AppMailchimpWrongResponseException(Exception):
    pass


class AppMailchimp:
    def _get_base_url(self):
        dc = settings.MAILCHIMP_API_KEY.split('-')[-1]

        return f'https://{dc}.api.mailchimp.com/3.0/'

    def format_url(self, url: str) -> str:
        return urljoin(self._get_base_url(), url.lstrip('/'))

    def _post(self, url: str, payload: dict):
        response = requests.post(
            url=self.format_url(url),
            auth=HTTPBasicAuth('user', settings.MAILCHIMP_API_KEY),
            json=payload,
        )
        if response.status_code != 200:
            raise AppMailchimpWrongResponseException(f'Wrong response from mailchimp: {response.status_code}. Response = {response.json()}')

        return response

    def subscribe(self, user: User):
        self._post(
            url=f'/lists/{settings.MAILCHIMP_CONTACT_LIST_ID}/members',
            payload={
                'email_address': user.email,
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': user.first_name,
                    'LNAME': user.last_name,
                },
            },
        )
