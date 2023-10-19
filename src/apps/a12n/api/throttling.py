from rest_framework.throttling import AnonRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class AuthAnonRateThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    """Throttle for any authorization views."""

    scope = "anon-auth"
