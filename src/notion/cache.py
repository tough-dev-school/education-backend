from typing import Callable

from django.core.cache import cache

from app.current_user import get_current_user
from notion.client import NotionClient
from notion.page import NotionPage

TIMEOUT = 60 * 60 * 24 * 2  # 2 days


def cache_key(page_id: str) -> str:
    return f'notion-page-cache--{page_id}'


def invalidate_cache(page_id: str) -> None:
    cache.delete(cache_key(page_id))


def fetch_page(page_id: str) -> Callable[[], NotionPage]:
    return lambda: NotionClient().fetch_page_recursively(page_id)


def current_user_is_staff() -> bool:
    user = get_current_user()
    if user:
        return user.is_staff

    return False


def get_cached_page(page_id: str) -> NotionPage:
    if current_user_is_staff():
        invalidate_cache(page_id)
        return fetch_page(page_id)()

    return cache.get_or_set(cache_key(page_id), fetch_page(page_id), TIMEOUT)


__all__ = [
    'get_cached_page',
]
