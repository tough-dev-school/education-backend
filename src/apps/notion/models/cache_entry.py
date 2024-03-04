from django.db.models import QuerySet
from django.utils import timezone

from core.models import TimestampedModel, models


class NotionCacheEntryQuerySet(QuerySet):
    def not_expired(self) -> "NotionCacheEntryQuerySet":
        time_now = timezone.now()
        return self.filter(expires__gt=time_now)


NotionCacheEntryManager = models.Manager.from_queryset(NotionCacheEntryQuerySet)


class NotionCacheEntry(TimestampedModel):
    objects = NotionCacheEntryManager()

    cache_key = models.CharField(max_length=255, unique=True, db_index=True)
    content = models.JSONField()
    expires = models.DateTimeField(db_index=True)

    def __str__(self) -> str:
        return self.cache_key
