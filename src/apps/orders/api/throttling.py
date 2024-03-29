from rest_framework.throttling import AnonRateThrottle

from core.throttling import ConfigurableThrottlingMixin


class PromocodeThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    scope = "promocode"


class PurchaseThrottle(ConfigurableThrottlingMixin, AnonRateThrottle):  # type: ignore
    scope = "purchase"
