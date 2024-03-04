from django.db.models import Index, UniqueConstraint

from core.models import TimestampedModel, models


class EmailLogEntry(TimestampedModel):
    email = models.CharField(max_length=255, null=False)
    template_id = models.CharField(max_length=255, null=False)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["email", "template_id"], name="Single template per email"),
        ]
        indexes = [
            Index(fields=["email", "template_id"]),
        ]
