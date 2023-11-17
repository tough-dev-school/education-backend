from rest_framework.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank


class DeprecatedBank(Bank):
    """Use it for banks that not used anymore."""

    name = _("Deprecated bank")

    def get_initial_payment_url(self) -> str:
        raise ValidationError("It's forbidden to place order for deprecated bank")

    def refund(self) -> None:
        raise ValidationError("The bank is deprecated. The orders for deprecated bank could not be refunded")
