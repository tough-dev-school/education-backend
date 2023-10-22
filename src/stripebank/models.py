from app.models import models
from app.models import TimestampedModel


class StripeNotification(TimestampedModel):
    order = models.ForeignKey("orders.Order", related_name="stripe_notifications", on_delete=models.PROTECT)
    stripe_id = models.CharField(db_index=True, max_length=256, unique=True)
    event_type = models.CharField(db_index=True, max_length=256)
    payment_intent = models.CharField(db_index=True, max_length=256)
    amount = models.DecimalField(decimal_places=2, max_digits=9)

    raw = models.JSONField(default=dict)
