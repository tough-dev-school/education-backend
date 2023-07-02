from typing import Any

from rest_framework.throttling import AnonRateThrottle

from django.conf import settings


class ConfigurableThrottlingMixin:
    def allow_request(self, *args: Any, **kwargs: dict[str, Any]) -> bool:
        if settings.DISABLE_THROTTLING:
            return True

        return super().allow_request(*args, **kwargs)  # type: ignore


class PublicIDThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    """Throttle for any authorization views."""

    scope = "public-id"


__all__ = [
    "ConfigurableThrottlingMixin",
    "PublicIDThrottle",
]
