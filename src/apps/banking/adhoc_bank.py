from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank


class AdhocBank(Bank):
    currency = "RUB"
    default_acquiring_percent = Decimal(0)
    default_currency_rate = Decimal(1)
    name = _("Adhoc")

    @property
    def is_partial_refund_available(self) -> bool:
        return True

    def get_initial_payment_url(self) -> str:
        raise ValidationError("The bank is not intended to by run by end-user")

    def refund(self, amount: Decimal | None = None) -> None:
        """No implementation is needed"""
