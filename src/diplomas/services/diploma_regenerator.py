from dataclasses import dataclass
from typing import cast

from django.db.models import QuerySet

from app.services import BaseService
from app.types import Language
from diplomas.models import Diploma
from diplomas.models import DiplomaTemplate
from diplomas.services.diploma_generator import DiplomaGenerator
from mailing.tasks import send_mail
from studying.models import Study
from users.models import User


@dataclass
class DiplomaRegenerator(BaseService):
    """Update and create student's diplomas.

    Tries to create diplomas on every possible language, to handle a case when student
    had a blank name for particular language, bot obtained it after the initial diploma
    generation. E.g. had only name in russian, and added an english name later.
    """

    student: User

    def act(self) -> None:
        generated_diplomas_count = 0

        for study in self.studies:
            generated_diplomas_count += self.generate_study_diplomas(study)

        if generated_diplomas_count > 0:
            self.notify()

    @property
    def studies(self) -> QuerySet[Study]:
        return Study.objects.filter(
            id__in=self.get_study_ids_for_diploma_regeneration(),
        ).select_related("course")

    def generate_study_diplomas(self, study: Study) -> int:
        count = 0
        for language in self.get_study_diploma_languages(study):
            self.regenerate(study, language)
            count += 1

        return count

    def get_study_ids_for_diploma_regeneration(self) -> list[int]:
        return list(
            Diploma.objects.filter(study__student=self.student)
            .filter_with_template()  # some diplomas have no template, can't regenerate them
            .order_by()
            .values_list("study__id", flat=True)
            .distinct("study__id"),
        )

    def get_study_diploma_languages(self, study: Study) -> list[Language]:
        study_diploma_languages = DiplomaTemplate.objects.filter(
            course=study.course,
            homework_accepted=study.homework_accepted,
            language__in=self.student.diploma_languages,
        ).values_list("language", flat=True)

        return [cast(Language, language) for language in study_diploma_languages]

    def notify(self) -> None:
        send_mail.delay(
            to=self.student.email,
            template_id="diplomas_regenerated",
            disable_antispam=True,
        )

    def regenerate(self, study: Study, language: Language) -> Diploma:
        return DiplomaGenerator(
            student=self.student,
            course=study.course,
            language=language,
        )()
