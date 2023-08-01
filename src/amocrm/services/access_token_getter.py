from urllib.parse import urljoin

import httpx
from httpx import Response

from django.conf import settings
from django.core.cache import cache

from app.exceptions import AppServiceException
from app.services import BaseService


class AmoCRMTokenGetterException(AppServiceException):
    """Raises when it's impossible to get a token"""


class AmoCRMTokenGetter(BaseService):
    """Returns access_token for amocrm http client"""

    def __init__(self) -> None:
        self.http = httpx.Client()
        self.url = urljoin(settings.AMOCRM_BASE_URL, "/oauth2/access_token")

    def act(self) -> str:
        access_token = cache.get("amocrm_access_token")
        if access_token is not None:
            return access_token

        refresh_token = cache.get("amocrm_refresh_token")
        if refresh_token is not None:
            return self.refresh_tokens()

        return self.setup_tokens()

    def refresh_tokens(self) -> str:
        """Refresh auth tokens"""
        response = self.http.post(
            url=self.url,
            data={
                "client_id": settings.AMOCRM_INTEGRATION_ID,
                "client_secret": settings.AMOCRM_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "code": cache.get("amocrm_refresh_token"),
                "redirect_uri": settings.AMOCRM_REDIRECT_URL,
            },
        )
        self.check_response(response)

        return self.save_tokens(response.json())

    def setup_tokens(self) -> str:
        """Setup initial auth tokens"""
        response = self.http.post(
            url=self.url,
            data={
                "client_id": settings.AMOCRM_INTEGRATION_ID,
                "client_secret": settings.AMOCRM_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": settings.AMOCRM_AUTHORIZATION_CODE,
                "redirect_uri": settings.AMOCRM_REDIRECT_URL,
            },
        )
        self.check_response(response)

        return self.save_tokens(response.json())

    @staticmethod
    def save_tokens(data: dict) -> str:
        timeout = int(data["expires_in"]) - 60 * 5  # remove token 5 min before expiration time
        cache.set("amocrm_access_token", data["access_token"], timeout=timeout)
        cache.set("amocrm_refresh_token", data["refresh_token"])
        return data["access_token"]

    @staticmethod
    def check_response(response: Response) -> None:
        if response.status_code != 200:
            raise AmoCRMTokenGetterException("Non-ok HTTP response when retrieving access token")
