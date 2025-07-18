from decimal import Decimal
from typing import Any

from apps.banking.models import Currency
from core.test.factory import register


@register
def currency(self: Any, name: str, rate: Decimal | None = None) -> Currency:  # noqa: ARG001
    rate = rate if rate is not None else Decimal(1)
    return Currency.objects.get_or_create(
        name=name,
        defaults={"rate": rate},
    )[0]
