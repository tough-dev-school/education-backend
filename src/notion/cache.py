from django.core.cache import cache

from notion.client import NotionClient
from notion.page import NotionPage

TIMEOUT = 60 * 60 * 24 * 2  # 2 days


def cache_key(page_id: str) -> str:
    return f'notion-page-cache--{page_id}'


def get_cached_page(page_id: str) -> NotionPage:
    cached = cache.get(cache_key(page_id))

    if cached:
        return cached

    page = NotionClient().fetch_page_recursively(page_id)

    cache.set(cache_key(page_id), page, TIMEOUT)

    return page


__all__ = [
    'get_cached_page',
]
