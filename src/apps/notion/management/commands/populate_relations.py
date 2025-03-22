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
            page = NotionPage.from_json(entry.content)
            count += 1

            for block in page.blocks:
                links = block.get_outgoing_links()
                for link in links:
                    self.stdout.write(f"\tGot {link}")
                    link_count += 1

            self.stdout.write(f"Processed cache entry: {entry.page_id}")

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {link_count} links in {count} cache entries"))
