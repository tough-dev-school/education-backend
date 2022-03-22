from app.models import TimestampedModel, models


class StripeNotification(TimestampedModel):
    order_id = models.CharField(db_index=True, max_length=256)
    stripe_id = models.CharField(db_index=True, max_length=256, unique=True)
    amount = models.DecimalField(decimal_places=2, max_digits=9)
    payment_status = models.CharField(db_index=True, max_length=256)
    status = models.CharField(db_index=True, max_length=256)

    raw = models.JSONField(default=dict)
