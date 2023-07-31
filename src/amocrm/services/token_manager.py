from urllib.parse import urljoin

import httpx
from httpx import Response

from django.conf import settings
from django.core.cache import cache

from app.exceptions import AppServiceException
from app.services import BaseService


class AmoCRMTokenManagerException(AppServiceException):
    """Raises when it's impossible to get a token"""


class AmoCRMTokenManager(BaseService):
    """Returns access_token for amocrm http client"""

    def __init__(self) -> None:
        self.http = httpx.Client()
        self.url = urljoin(settings.AMOCRM_BASE_URL, "/oauth2/access_token")

    def act(self) -> str:
        refresh_token = cache.get("amocrm_refresh_token")
        if refresh_token is None:
            self.setup_tokens()

        access_token = cache.get("amocrm_access_token")
        if access_token is None:
            self.refresh_tokens()

        return cache.get("amocrm_access_token")

    def refresh_tokens(self) -> None:
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

    def setup_tokens(self) -> None:
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
    def save_tokens(data: dict) -> None:
        timeout = int(data["expires_in"]) - 60 * 5  # refresh tokens 5 min before expiration time
        cache.set("amocrm_access_token", data["access_token"], timeout=timeout)
        cache.set("amocrm_refresh_token", data["refresh_token"])

    @staticmethod
    def check_response(response: Response) -> None:
        if response.status_code != 200:
            raise AmoCRMTokenManagerException("Non-ok HTTP response when retrieving access token")
