from typing import Any

from apps.banking.models import Acquiring, CurrencyRate
from core.test.factory import register


@register
def currency_rate(self: Any, **kwargs: dict[str, Any]) -> CurrencyRate:
    return self.mixer.blend("banking.CurrencyRate", **kwargs)


@register
def acquiring(self: Any, **kwargs: dict[str, Any]) -> Acquiring:
    return self.mixer.blend("banking.Acquiring", **kwargs)
