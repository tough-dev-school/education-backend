from rest_framework.throttling import UserRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class NotionThrottle(ConfigurableThrottlingMixin, UserRateThrottle):  # type: ignore
    """Throttle for any authorization views."""

    scope = "notion-materials"
