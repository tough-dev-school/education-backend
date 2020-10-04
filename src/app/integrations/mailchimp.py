import hashlib
from urllib.parse import urljoin

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

from users.models import User


class AppMailchimpWrongResponseException(Exception):
    pass


class AppMailchimpNotFoundException(AppMailchimpWrongResponseException):
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

    def _get(self, url: str):
        response = requests.get(
            url=self.format_url(url),
            auth=HTTPBasicAuth('user', settings.MAILCHIMP_API_KEY),
        )

        if response.status_code == 404:
            raise AppMailchimpNotFoundException(f'Got 404 response from mailchimp: {response.status_code}. Response = {response.json()}')

        if response.status_code != 200:
            raise AppMailchimpWrongResponseException(f'Wrong response from mailchimp: {response.status_code}. Response = {response.json()}')

        return response

    def subscribe(self, user: User):
        if not self.member_exists(user.email):
            self._subscribe(user)

    def _subscribe(self, user: User):
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

    def member_exists(self, email: str) -> bool:
        subscriber_hash = hashlib.md5(email.encode()).hexdigest()
        try:
            self._get(f'/lists/{settings.MAILCHIMP_CONTACT_LIST_ID}/members/{subscriber_hash}')
        except AppMailchimpNotFoundException:
            return False

        return True
