from collections.abc import Callable
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

from apps.notion.client import NotionClient
from apps.notion.models import NotionCacheEntry
from apps.notion.page import NotionPage
from apps.notion.types import NotionId
from core.current_user import get_current_user

TIMEOUT = 60 * 60 * 24 * 365 * 5  # 5 years


class NotionCache:
    """Database notion cache. We call it cache for the API, actualy we store all notion pages in the DB to own our data

    Notion page_id is used as the cache key
    """

    def set(self, page_id: NotionId, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        expires_datetime = self.get_expires_time()
        content = self.get_content_as_notion_page(content)
        content_to_save = content.to_json()
        NotionCacheEntry.objects.update_or_create(page_id=page_id, defaults=dict(content=content_to_save, expires=expires_datetime))
        return content

    def get(self, page_id: NotionId) -> NotionPage | None:
        cache_entry = self._get(page_id)
        if cache_entry:
            return NotionPage.from_json(data=cache_entry.content, kwargs={"id": cache_entry.page_id})

    def get_or_set(self, page_id: NotionId, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        cache_entry = self._get(page_id)
        if cache_entry:
            return NotionPage.from_json(data=cache_entry.content, kwargs={"id": cache_entry.page_id})
        return self.set(page_id, content)

    @staticmethod
    def _get(page_id: NotionId) -> NotionCacheEntry | None:
        return NotionCacheEntry.objects.not_expired().filter(page_id=page_id).first()

    @staticmethod
    def get_content_as_notion_page(content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        return content() if callable(content) else content

    @staticmethod
    def get_expires_time() -> datetime:
        return timezone.now() + timedelta(seconds=TIMEOUT)


cache = NotionCache()


def fetch_page(page_id: NotionId) -> Callable[[], NotionPage]:
    return lambda: NotionClient().fetch_page(page_id)


def should_bypass_cache() -> bool:
    if settings.NOTION_CACHE_ONLY:
        return False

    user = get_current_user()
    if user:
        return user.is_staff

    return False


def get_cached_page_or_fetch(page_id: NotionId) -> NotionPage:
    if should_bypass_cache():
        page = fetch_page(page_id)()
        cache.set(page_id, page)
        return page

    return cache.get_or_set(page_id, fetch_page(page_id))


__all__ = [
    "get_cached_page_or_fetch",
]
