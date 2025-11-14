from django.utils import timezone

from apps.notion.types import NotionId
from core.models import TimestampedModel, models


class NotionCacheEntryStatus(TimestampedModel):
    """Human-readable status of entry fetching"""

    page_id = models.CharField(max_length=255, unique=True, db_index=True)
    fetch_started = models.DateTimeField(null=True, db_index=True)
    fetch_complete = models.DateTimeField(null=True, db_index=True)

    @classmethod
    def log_start(cls, page_id: NotionId) -> None:
        status, _ = cls.objects.get_or_create(page_id=page_id)

        status.fetch_started = timezone.now()
        status.fetch_complete = None

        status.save(update_fields=["fetch_started", "fetch_complete"])

    @classmethod
    def log_completion(cls, page_id: NotionId) -> None:
        status = cls.objects.get(page_id=page_id)

        status.fetch_complete = timezone.now()
        status.save(update_fields=["fetch_complete"])
