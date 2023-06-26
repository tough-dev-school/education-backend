from datetime import datetime
from datetime import timedelta
from typing import Callable

from django.db.models import QuerySet
from django.utils import timezone

from app.current_user import get_current_user
from notion.client import NotionClient
from notion.models import NotionCacheEntry
from notion.page import NotionPage

TIMEOUT = 60 * 60 * 24 * 14  # 14 days


class NotionCache:
    cache: QuerySet[NotionCacheEntry] = NotionCacheEntry.objects.all()

    def set(self, cache_key: str, content: NotionPage | Callable[[], NotionPage], timeout: int = TIMEOUT) -> None:
        expires_datetime = self.get_expires_time(timeout)
        content = self.content_as_notion_page(content)
        content_to_save = self.notion_page_to_dict(content)
        self.cache.update_or_create(cache_key=cache_key, defaults=dict(content=content_to_save, expires=expires_datetime))

    def get(self, cache_key) -> NotionPage | None:
        cache_entry = self._get(cache_key)
        if cache_entry:
            return self.dict_to_notion_page(cache_entry.content)

    def get_or_set(self, cache_key: str, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        cache_entry = self._get(cache_key)
        if cache_entry:
            return self.dict_to_notion_page(cache_entry.content)
        content = self.content_as_notion_page(content)
        self.set(cache_key, content, timeout)
        return content

    def delete(self, cache_key: str) -> None:
        cache_entry = self.cache.filter(cache_key=cache_key).first()
        if cache_entry:
            cache_entry.delete()

    def _get(self, cache_key: str) -> NotionCacheEntry | None:
        cache_entry = self.cache.filter(cache_key=cache_key).first()
        if not cache_entry:
            return None
        if cache_entry.expires < timezone.now():
            cache_entry.delete()
            return None
        return cache_entry

    @classmethod
    def get_expires_time(cls, timeout: int) -> datetime:
        return timezone.now() + timedelta(seconds=timeout)

    @classmethod
    def content_as_notion_page(cls, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        return content() if callable(content) else content

    @classmethod
    def notion_page_to_dict(cls, content: NotionPage) -> dict:
        return content.as_dict()

    @classmethod
    def dict_to_notion_page(cls, content: dict) -> NotionPage:
        return NotionPage.from_dict(content)


cache = NotionCache()


def fetch_page(page_id: str) -> Callable[[], NotionPage]:
    return lambda: NotionClient().fetch_page_recursively(page_id)


def cache_disabled() -> bool:
    user = get_current_user()
    if user:
        return user.is_staff

    return False


def get_cached_page(page_id: str) -> NotionPage:
    if cache_disabled():
        page = fetch_page(page_id)()
        cache.set(page_id, page, TIMEOUT)
        return page

    return cache.get_or_set(page_id, fetch_page(page_id), TIMEOUT)


__all__ = [
    "get_cached_page",
]
