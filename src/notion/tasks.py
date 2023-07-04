from app.celery import celery
from notion.cache import cache
from notion.client import NotionClient
from notion.models import Material


@celery.task(rate_limit="6/m", acks_late=True)
def update_cache_notion_material(page_id: str) -> None:
    page = NotionClient().fetch_page_recursively(page_id)
    cache.set(page_id, page)


@celery.task
def update_cache_for_all_active_notion_materials() -> None:
    page_ids = Material.objects.active().values_list("page_id", flat=True).distinct()
    for page_id in page_ids:
        update_cache_notion_material.delay(page_id)
