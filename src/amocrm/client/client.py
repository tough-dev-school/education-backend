from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable

from django.conf import settings
from django.core.cache import cache

from amocrm.client.http import AmoCRMHTTP


def auto_refresh_token(function: Callable) -> Any:
    @wraps(function)
    def wrapper(client: "AmoCRMClient", *args: Any, **kwargs: Any) -> Any:
        if cache.get("amocrm_access_token") is None:
            client.refresh_tokens()
        return function(client, *args, **kwargs)

    return wrapper


@dataclass
class AmoCRMClient:
    """
    Client to deal with amoCRM with autologin.

    client = AmoCRMClient()
    client.create_company(customer)
    """

    http = AmoCRMHTTP()

    @classmethod
    def refresh_tokens(cls) -> None:
        """Refresh auth tokens"""
        got = cls.http.post(
            url="/oauth2/access_token",
            data={
                "client_id": settings.AMOCRM_INTEGRATION_ID,
                "client_secret": settings.AMOCRM_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "code": cache.get("amocrm_refresh_token"),
                "redirect_uri": settings.AMOCRM_REDIRECT_URL,
            },
        )

        timeout = int(got["expires_in"]) - 60 * 5  # refresh tokens 5 min before expiration time
        cache.set("amocrm_access_token", got["access_token"], timeout=timeout)
        cache.set("amocrm_refresh_token", got["refresh_token"])

    @classmethod
    def enable_customers(cls) -> None:
        """Requires to create/update customers"""
        cls.http.patch(url="/api/v4/customers/mode", data={"mode": "segments", "is_enabled": True})
