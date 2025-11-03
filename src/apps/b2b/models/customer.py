from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from core.models import TimestampedModel, models


def validate_customer_code(value: str) -> None:
    """Validate that the customer code contains only digits, '-', and '.'"""
    if value and not all(c.isdigit() or c in "-." for c in value):
        raise ValidationError(_("Customer code can only contain digits, '-', and '.'"))


class Customer(TimestampedModel):
    name = models.CharField(verbose_name=pgettext_lazy("deals", "Customer name"), max_length=255)
    tin = models.CharField(
        verbose_name=_("TIN"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        validators=[validate_customer_code],
        help_text=_("Should be Unique"),
    )

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
