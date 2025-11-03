from decimal import Decimal
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.banking import currency
from core.models import TimestampedModel, models

if TYPE_CHECKING:
    from django_stubs_ext import StrPromise


class Deal(TimestampedModel):
    customer = models.ForeignKey("b2b.Customer", on_delete=models.CASCADE, verbose_name=_("Customer"))
    course = models.ForeignKey("products.Course", on_delete=models.PROTECT)
    author = models.ForeignKey("users.User", related_name="created_deals", verbose_name=_("Deal author"), on_delete=models.PROTECT, editable=False)
    comment = models.TextField(_("Comment"), blank=True)
    completed = models.DateTimeField(_("Date when the deal got completed"), null=True, blank=True)
    canceled = models.DateTimeField(_("Date when the deal got canceled"), null=True, blank=True)
    shipped_without_payment = models.DateTimeField(_("Date when the deal got shipped without payment"), null=True, blank=True)
    price = models.DecimalField(_("Price"), max_digits=9, decimal_places=2)
    currency = models.CharField(_("Currency"), choices=currency.CurrencyCodes.choices(), default="RUB")
    currency_rate_on_creation = models.DecimalField(max_digits=9, decimal_places=2, null=True)

    class Meta:
        verbose_name = _("Deal")
        verbose_name_plural = _("Deals")

    def __str__(self) -> str:
        return self.customer.name

    def get_status_representation(self) -> "StrPromise":
        """Text representation of date-based DB fields"""
        if self.canceled is not None:
            return pgettext_lazy("deals", "Canceled")

        if self.completed is not None:
            return pgettext_lazy("deals", "Complete")

        if self.shipped_without_payment is not None:
            return pgettext_lazy("deals", "Shipped without payment")

        return pgettext_lazy("deals", "In progress")

    def get_single_order_price(self) -> Decimal:
        try:
            return Decimal(self.price * currency.get_rate_or_default(self.currency) / self.students.count())
        except ArithmeticError:
            return Decimal(0)
