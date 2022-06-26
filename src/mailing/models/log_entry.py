from app.models import TimestampedModel, models


class EmailLogEntry(TimestampedModel):
    email = models.CharField(max_length=255, null=False)
    template_id = models.CharField(max_length=255, null=False)

    class Meta:
        index_together = ['email', 'template_id']
        unique_together = ['email', 'template_id']
