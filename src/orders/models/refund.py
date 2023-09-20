from django.db import models

from app.models import TimestampedModel


class Refund(TimestampedModel):
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="refund")
    author = models.ForeignKey("users.User", on_delete=models.RESTRICT, related_name="order_refunds")
    author_ip = models.GenericIPAddressField()
    bank_confirmation_received = models.BooleanField(default=False, verbose_name="Bank refund confirmation")

    class Meta:
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"Refund for order #{self.order.pk}, by {self.author}"
