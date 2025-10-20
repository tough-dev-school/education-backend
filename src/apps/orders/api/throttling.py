from rest_framework.throttling import AnonRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class OrderDraftThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):
    scope = "order-draft"


class PurchaseThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):
    scope = "purchase"
