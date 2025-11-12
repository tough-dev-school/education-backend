from django.db.models import QuerySet

from core.models import TimestampedModel, models


class NotionCacheEntryQuerySet(QuerySet): ...


NotionCacheEntryManager = models.Manager.from_queryset(NotionCacheEntryQuerySet)


class NotionCacheEntry(TimestampedModel):
    objects = NotionCacheEntryManager()

    page_id = models.CharField(max_length=255, unique=True, db_index=True)
    content = models.JSONField()

    def __str__(self) -> str:
        return self.page_id
