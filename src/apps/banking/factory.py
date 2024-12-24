from typing import Any

from apps.banking.models import CurrencyRate
from core.test.factory import register


@register
def currency_rate(self: Any, **kwargs: dict[str, Any]) -> CurrencyRate:
    return self.mixer.blend("banking.CurrencyRate", **kwargs)
