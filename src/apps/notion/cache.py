from collections.abc import Callable

from apps.notion.client import NotionClient
from apps.notion.models import NotionCacheEntry, NotionCacheEntryStatus
from apps.notion.page import NotionPage
from apps.notion.types import NotionId


class NotionCache:
    """Database notion cache. We call it cache for the API, actualy we store all notion pages in the DB to own our data

    Notion page_id is used as the cache key
    """

    def set(self, page_id: NotionId, content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        content = self.get_content_as_notion_page(content)
        content_to_save = content.to_json()
        NotionCacheEntry.objects.update_or_create(page_id=page_id, defaults=dict(content=content_to_save))
        return content

    def get(self, page_id: NotionId) -> NotionPage | None:
        cache_entry = self._get(page_id)
        if cache_entry:
            return NotionPage.from_json(data=cache_entry.content, kwargs={"id": cache_entry.page_id})

    @staticmethod
    def _get(page_id: NotionId) -> NotionCacheEntry | None:
        return NotionCacheEntry.objects.filter(page_id=page_id).first()

    @staticmethod
    def get_content_as_notion_page(content: NotionPage | Callable[[], NotionPage]) -> NotionPage:
        return content() if callable(content) else content


cache = NotionCache()  # global cache


def get_cached_page_or_fetch(page_id: NotionId) -> NotionPage:
    page = cache.get(page_id)
    if page is not None:
        return page

    NotionCacheEntryStatus.log_start(page_id)
    page = NotionClient().fetch_page(page_id)
    cache.set(page_id, page)
    NotionCacheEntryStatus.log_completion(page_id)

    return page


__all__ = [
    "get_cached_page_or_fetch",
]
