from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class Customer(TimestampedModel):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")


class Deal(TimestampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Course", on_delete=models.PROTECT)
    author = models.ForeignKey("users.User", related_name="created_deals", verbose_name=_("Deal author"), on_delete=models.PROTECT, editable=False)
    comment = models.TextField(_("Comment"), blank=True)
    completed = models.DateTimeField(_("Date when the deal got completed"), null=True, blank=True)
    canceled = models.DateTimeField(_("Date when the deal got canceled"), null=True, blank=True)
    price = models.DecimalField(_("Price"), max_digits=9, decimal_places=2)

    class Meta:
        verbose_name = _("Deal")
        verbose_name_plural = _("Deals")

    def __str__(self) -> str:
        return f"{self.customer.name} {self.price}"


class Student(TimestampedModel):
    user = models.ForeignKey("users.User", on_delete=models.PROTECT)
    deal = models.ForeignKey(Deal, related_name="students", on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Student")
        verbose_name_plural = _("Students")

    def __str__(self) -> str:
        return str(self.user)
