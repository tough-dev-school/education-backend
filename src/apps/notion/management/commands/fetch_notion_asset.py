from pathlib import Path
from typing import Any, no_type_check

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.notion.http import fetch_asset


class Command(BaseCommand):
    help = "Fetches a Notion asset via our middleware"

    def add_arguments(self, parser):
        parser.add_argument("url", type=str, help="Notion asset URL to fetch")
        parser.add_argument("--output", type=str, help="Output file path (default: save to current directory with original filename)")

    @no_type_check
    def handle(self, *args: Any, **options: dict[str, Any]) -> None:
        url = options["url"]
        output_path = options["output"]

        self.stdout.write(f"Fetching asset via {settings.NOTION_MIDDLEWARE_URL}")
        content = fetch_asset(url)

        if output_path is None:
            # Extract filename from URL if no output path is specified
            filename = url.split("/")[-1].split("?")[0]
            output_path = Path.cwd() / filename

        with open(output_path, "wb") as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"Successfully fetched asset and saved to {output_path}"))
        self.stdout.write(f"Asset size: {len(content)} bytes")
