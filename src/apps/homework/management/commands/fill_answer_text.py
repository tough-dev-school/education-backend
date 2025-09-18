from django.core.management.base import BaseCommand

from apps.homework.models import Answer
from core.prosemirror import prosemirror_to_text


class Command(BaseCommand):
    help = "Convert ProseMirror content to text for homework answers where text is empty and content is not"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be converted without making changes",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        # Find answers where text is empty but content is not
        answers = Answer.objects.filter(text__in=["", None], content__isnull=False).exclude(content={})

        total_count = answers.count()

        if total_count == 0:
            self.stdout.write(self.style.WARNING("No answers found that need conversion."))
            return

        self.stdout.write(f"Found {total_count} answers to convert.")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made."))

        converted_count = 0

        for answer in answers:
            if answer.content:
                converted_text = prosemirror_to_text(answer.content)

                if dry_run:
                    self.stdout.write(f"Would convert answer {answer.pk}: {len(converted_text)} characters")
                else:
                    answer.text = converted_text
                    answer.save(update_fields=["text"])

                converted_count += 1

        # Final summary
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN COMPLETE: Would convert {converted_count} answers."))
        else:
            self.stdout.write(self.style.SUCCESS(f"CONVERSION COMPLETE: Converted {converted_count} answers."))
