from core.models import TimestampedModel, models


class StripeNotification(TimestampedModel):
    order = models.ForeignKey("orders.Order", related_name="stripe_notifications", null=True, on_delete=models.PROTECT)
    stripe_id = models.CharField(db_index=True, max_length=256, unique=True)
    event_type = models.CharField(db_index=True, max_length=256)
    payment_intent = models.CharField(db_index=True, max_length=256, default="")
    amount = models.DecimalField(decimal_places=2, max_digits=9, default=0)

    raw = models.JSONField(default=dict)
