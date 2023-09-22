from django.db import models

from app.models import TimestampedModel


class RefundLogEntry(TimestampedModel):
    """Log entry for all non zero priced refunds."""

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="refund_log_entries")
    author = models.ForeignKey("users.User", on_delete=models.RESTRICT, related_name="refund_log_entries")

    class Meta:
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"Refund for order #{self.order.pk}, by {self.author}"
