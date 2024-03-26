from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.banking.selector import BANK_CHOICES
from core.models import TimestampedModel


class Refund(TimestampedModel):
    order = models.ForeignKey("orders.Order", verbose_name=_("Order"), on_delete=models.CASCADE, related_name="refunds")
    amount = models.DecimalField(_("Amount"), max_digits=9, decimal_places=2)
    author = models.ForeignKey("users.User", verbose_name=_("Author"), on_delete=models.PROTECT, editable=False, related_name="created_refunds")
    bank_id = models.CharField(_("Order bank at the moment of refund"), choices=BANK_CHOICES, blank=True, max_length=32)

    class Meta:
        verbose_name = _("Refund")
        verbose_name_plural = _("Refunds")

    def __str__(self) -> str:
        return f"{self.order} {self.amount}"
