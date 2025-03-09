from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank


class B2BBank(Bank):
    name = _("B2B Bank")

    def get_initial_payment_url(self) -> str:
        raise ValidationError("B2B Bank does not support end-user payments")
