from rest_framework.throttling import UserRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class NotionThrottle(ConfigurableThrottlingMixin, UserRateThrottle):  # type: ignore
    """Throttle downloading materials"""

    scope = "notion-materials"
