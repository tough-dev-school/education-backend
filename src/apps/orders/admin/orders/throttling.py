from rest_framework.throttling import UserRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class OrderRefundActionThrottle(ConfigurableThrottlingMixin, UserRateThrottle):  # type: ignore
    """Throttle for order's admin action `refund`."""

    scope = "order-refund"
