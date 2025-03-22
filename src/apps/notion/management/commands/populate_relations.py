from typing import Any

from django.core.management.base import BaseCommand

from apps.notion.models.cache_entry import NotionCacheEntry
from apps.notion.page import NotionPage


class Command(BaseCommand):
    help_text = "Populates notion material relations from current cache"

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        count = 0
        link_count = 0
        for entry in NotionCacheEntry.objects.iterator():
            page = NotionPage.from_json(data=entry.content, kwargs={"id": entry.page_id})
            count += 1

            page.save_relations()

            self.stdout.write(f"Processed cache entry: {entry.page_id}")

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {link_count} links in {count} cache entries"))
