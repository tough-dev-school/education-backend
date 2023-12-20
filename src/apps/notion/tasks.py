import httpx

from django.apps import apps

from apps.notion.exceptions import NotionError
from core.celery import celery


@celery.task(
    rate_limit="6/m",
    acks_late=True,
    name="notion.update_cache",
    autoretry_for=[httpx.HTTPError, NotionError],
    retry_kwargs={
        "max_retries": 5,
        "countdown": 5,
    },
)
def update_cache(page_id: str) -> None:
    from apps.notion.cache import cache
    from apps.notion.client import NotionClient

    page = NotionClient().fetch_page_recursively(page_id)
    cache.set(page_id, page)


@celery.task(name="notion.update_cache_for_all_pages")
def update_cache_for_all_pages() -> None:
    page_ids = apps.get_model("notion.Material").objects.active().values_list("page_id", flat=True).distinct()

    for page_id in page_ids:
        update_cache.delay(page_id=page_id)


@celery.task(
    rate_limit="1/s",
    name="notion.save_asset",
    autoretry_for=[httpx.HTTPError, NotionError],
    retry_kwargs={
        "max_retries": 5,
        "countdown": 5,
    },
)
def save_asset(url: str, original_url: str) -> None:
    from apps.notion.assets import save_asset as _save_asset

    _save_asset(url=url, original_url=original_url)
