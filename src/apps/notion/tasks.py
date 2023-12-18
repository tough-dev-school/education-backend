from apps.notion.cache import cache
from apps.notion.client import NotionClient
from apps.notion.models import Material
from core.celery import celery


@celery.task(
    rate_limit="6/m",
    acks_late=True,
    name="notion.update_cache",
)
def update_cache(page_id: str) -> None:
    page = NotionClient().fetch_page_recursively(page_id)
    cache.set(page_id, page)


@celery.task(name="notion.update_cache_for_all_pages")
def update_cache_for_all_pages() -> None:
    page_ids = Material.objects.active().values_list("page_id", flat=True).distinct()
    for page_id in page_ids:
        update_cache.delay(page_id=page_id)
