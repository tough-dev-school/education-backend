from django.core.management.base import BaseCommand

from apps.homework.models import Answer, AnswerCrossCheck


class Command(BaseCommand):
    help = "Restore checked dates on AnswerCrossCheck based on child Answer records"

    def handle(self, *args, **options):
        # Get all cross-checks that need updating
        crosschecks_to_update = []

        for crosscheck in AnswerCrossCheck.objects.filter(checked__isnull=True).select_related("answer", "checker"):
            # Find direct child answers where the crosscheck checker is the author and parent is the crosscheck answer
            child_answers = Answer.objects.filter(
                parent=crosscheck.answer,
                author=crosscheck.checker,
            )

            if child_answers.exists():
                # Found at least one matching child answer - use its modified date
                crosscheck.checked = child_answers.latest("modified").modified
                crosschecks_to_update.append(crosscheck)

        # Bulk update all found crosschecks
        if crosschecks_to_update:
            AnswerCrossCheck.objects.bulk_update(crosschecks_to_update, ["checked"])
            self.stdout.write(self.style.SUCCESS(f"Successfully updated {len(crosschecks_to_update)} crosschecks"))
        else:
            self.stdout.write(self.style.SUCCESS("No crosschecks needed updating"))
