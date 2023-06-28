from typing import Any

from django.core.management.base import BaseCommand

from notion import tasks


class Command(BaseCommand):
    help = "Updates cache for all active Notion materials"

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        confirm = input("Are you sure you want to update cache for all active Notion materials? (y/n): ")
        if confirm.lower() not in ("y", "yes"):
            self.stdout.write(self.style.WARNING("Cache update cancelled"))
            return

        tasks.update_cache_for_all_active_notion_materials.delay()
        self.stdout.write(self.style.SUCCESS("Task for updating cache is made. Cache will be updated soon"))
