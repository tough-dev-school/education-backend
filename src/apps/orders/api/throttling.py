from rest_framework.throttling import AnonRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class OrderDraftThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    scope = "order-draft"


class PurchaseThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    scope = "purchase"
