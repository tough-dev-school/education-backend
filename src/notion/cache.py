from datetime import datetime
from datetime import timedelta
from typing import Callable

from django.conf import settings
from django.utils import timezone

from app.current_user import get_current_user
from notion.client import NotionClient
from notion.models import NotionCacheEntry
from notion.page import NotionPage

TIMEOUT = 60 * 60 * 24 * 365 * 5  # 5 years


class NotionCache:
    def set(self, cache_key: str, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        expires_datetime = self.get_expires_time()
        content = self.get_content_as_notion_page(content)
        content_to_save = content.to_json()
        NotionCacheEntry.objects.update_or_create(cache_key=cache_key, defaults=dict(content=content_to_save, expires=expires_datetime))
        return content

    def get(self, cache_key: str) -> NotionPage | None:
        cache_entry = self._get(cache_key)
        if cache_entry:
            return NotionPage.from_json(cache_entry.content)

    def get_or_set(self, cache_key: str, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        cache_entry = self._get(cache_key)
        if cache_entry:
            return NotionPage.from_json(cache_entry.content)
        return self.set(cache_key, content)

    @staticmethod
    def _get(cache_key: str) -> NotionCacheEntry | None:
        return NotionCacheEntry.objects.not_expired().filter(cache_key=cache_key).first()

    @staticmethod
    def get_content_as_notion_page(content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        return content() if callable(content) else content

    @staticmethod
    def get_expires_time() -> datetime:
        return timezone.now() + timedelta(seconds=TIMEOUT)


cache = NotionCache()


def fetch_page(page_id: str) -> Callable[[], NotionPage]:
    return lambda: NotionClient().fetch_page_recursively(page_id)


def should_bypass_cache() -> bool:
    if settings.NOTION_CACHE_ONLY:
        return False

    user = get_current_user()
    if user:
        return user.is_staff

    return False


def get_cached_page(page_id: str) -> NotionPage:
    if should_bypass_cache():
        page = fetch_page(page_id)()
        cache.set(page_id, page)
        return page

    return cache.get_or_set(page_id, fetch_page(page_id))


__all__ = [
    "get_cached_page",
]
