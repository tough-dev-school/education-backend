from app.models import models
from app.models import TimestampedModel


class TriggerLogEntry(TimestampedModel):
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="trigger_log")
    trigger = models.CharField(max_length=255, db_index=True)

    class Meta:
        unique_together = [
            ("order", "trigger"),
        ]
