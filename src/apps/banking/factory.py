from typing import Any

from apps.banking.models import Currency
from core.test.factory import register


@register
def currency(self: Any, **kwargs: dict[str, Any]) -> Currency:
    return self.mixer.blend("banking.Currency", **kwargs)
