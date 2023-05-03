from rest_framework.throttling import AnonRateThrottle

from django.conf import settings


class ConfigurableThrottlingMixin:
    def allow_request(self, *args, **kwargs):
        if settings.DISABLE_THROTTLING:
            return True

        return super().allow_request(*args, **kwargs)


class PublicIDThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):
    """Throttle for any authorization views."""

    scope = "public-id"


__all__ = [
    "ConfigurableThrottlingMixin",
    "PublicIDThrottle",
]
