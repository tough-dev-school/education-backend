from datetime import timedelta

import httpx

from django.conf import settings
from django.core.cache import cache

from banking.atol.exceptions import AtolAuthError


def get_atol_token() -> str:
    return cache.get_or_set(  # type: ignore
        key="ATOL_AUTH_TOKEN",
        default=fetch,
        timeout=timedelta(hours=14).seconds,
    )


def fetch() -> str:
    response = httpx.post(
        url="https://online.atol.ru/possystem/v4/getToken",
        json={
            "login": settings.ATOL_LOGIN,
            "pass": settings.ATOL_PASSWORD,
        },
    )

    data = response.json()

    if response.status_code != 200 or data["error"] is not None:
        raise AtolAuthError("Atol error: %s (code: %s)", data["error"]["text"], data["error"]["error_id"])

    return data["token"]
