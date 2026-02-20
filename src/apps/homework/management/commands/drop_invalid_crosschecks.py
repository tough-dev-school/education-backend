from django.core.management.base import BaseCommand

from apps.homework.models import AnswerCrossCheck


class Command(BaseCommand):
    help = "Drop crosschecks that were incorrectly created for non-root answers"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting",
        )

    def handle(self, *args, **options) -> None:
        invalid_crosschecks = AnswerCrossCheck.objects.filter(answer__parent__isnull=False)
        count = invalid_crosschecks.count()

        if options["dry_run"]:
            self.stdout.write(f"Would delete {count} invalid crosschecks (linked to non-root answers)")
            return

        deleted, _ = invalid_crosschecks.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} invalid crosschecks"))
