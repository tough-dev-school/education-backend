from rest_framework.throttling import AnonRateThrottle

from app.throttling import ConfigurableThrottlingMixin


class PromocodeThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    """Throttle for any authorization views."""

    scope = "promocode"
