from typing import Any

from django.core.management.base import BaseCommand

from apps.notion.cache import cache
from apps.notion.types import NotionId
from core.celery import celery


class Command(BaseCommand):
    help = "Creates a NotionPage from cache and runs post-processing mechanisms. Use it to debug after_fetch()"

    def add_arguments(self, parser):
        parser.add_argument("page_id", type=str, help="Notion page ID to fetch from cache")

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        page_id = options["page_id"]

        page = cache.get(NotionId(page_id))

        if page is None:
            self.stdout.write(self.style.ERROR(f"Page with ID {page_id} not found in cache"))
            return

        self.stdout.write(self.style.SUCCESS(f"Successfully created NotionPage from cache: {page_id}"))
        self.stdout.write(f"Page title: {page.title}")
        self.stdout.write(f"Blocks count: {len(page.blocks)}")

        self.stdout.write("\nPerforming after_fetch...")
        celery.conf.update(task_always_eager=True)
        page.after_fetch()
        self.stdout.write(self.style.SUCCESS("OK"))
