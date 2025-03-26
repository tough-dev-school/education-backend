import contextlib
from typing import no_type_check

from django.core.management import BaseCommand
from tqdm import tqdm

from apps.homework.models import Answer
from apps.studying.models import Study


class Command(BaseCommand):
    help = "Migrate Answer objects to link them with corresponding Study objects"

    @no_type_check
    def handle(self, *args, **options):
        def find_study(answer):
            for course_id in answer.question.courses.values_list("id", flat=True):
                with contextlib.suppress(Study.DoesNotExist):
                    return Study.objects.get(course=course_id, student_id=answer.author_id)

        answers = Answer.objects.select_related("question").prefetch_related("question__courses")
        total = answers.count()

        self.stdout.write(self.style.NOTICE(f"Found {total} answers to process"))

        updated_count = 0
        for answer in tqdm(answers.iterator(), total=total, desc="Migrating answers to studies"):
            study = find_study(answer)
            if study is not None:
                answer.study = study
                answer.save(update_fields=["study"])
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"Migration completed. Updated {updated_count} answers with study references."))
