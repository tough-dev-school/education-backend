import json
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.homework.models import Answer


class Command(BaseCommand):
    help = "Export JSON content from homework Answer instances to prosemirror-examples.json"

    def handle(self, *args, **options) -> None:
        self.stdout.write("Starting export of ProseMirror examples...")

        answers_with_json = Answer.objects.filter(content__isnull=False).exclude(content={})

        if not answers_with_json.exists():
            self.stdout.write(self.style.WARNING("No Answer instances found with JSON content"))
            return

        examples = []
        for answer in answers_with_json:
            examples.append({"id": str(answer.slug), "created": answer.created.isoformat(), "content": answer.content})

        output_path = Path("prosemirror-examples.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(examples, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Successfully exported {len(examples)} examples to {output_path.absolute()}"))
