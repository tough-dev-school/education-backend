from rest_framework.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

from apps.banking.base import Bank


class ManualBank(Bank):
    """Bank for orders set paid manually."""

    name = _("Manual")

    def get_initial_payment_url(self) -> str:
        raise ValidationError("Initial payment URL is not available for manual bank")
