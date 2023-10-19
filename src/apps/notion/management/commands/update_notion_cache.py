from typing import Any

from django.core.management.base import BaseCommand

from apps.notion import tasks


class Command(BaseCommand):
    help = "Updates cache for all active Notion materials"

    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        tasks.update_cache_for_all_active_notion_materials.delay()
        self.stdout.write(self.style.SUCCESS("Task for updating cache is made. Cache will be updated soon"))
