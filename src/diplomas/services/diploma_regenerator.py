from typing import cast

import contextlib
from dataclasses import dataclass
from django.db.models import QuerySet

from app.types import Language
from diplomas.models import Diploma, DiplomaTemplate
from diplomas.services.diploma_generator import DiplomaGenerator
from mailing.tasks import send_mail
from studying.models import Study
from users.models import User


@dataclass
class DiplomaRegenerator:
    student: User

    def __post_init__(self) -> None:
        self.regenerated_diplomas_counter = 0

    def __call__(self) -> None:
        for study in self.studies_with_diplomas:
            self.generate_study_diplomas(study)

        if self.regenerated_diplomas_counter > 0:
            self.notify()

    @property
    def studies_with_diplomas(self) -> QuerySet[Study]:
        return Study.objects.filter(
            student=self.student,
            diploma__isnull=False,
        ).distinct().select_related('course')

    def generate_study_diplomas(self, study: Study) -> None:
        for language in self.get_study_diploma_languages(study):
            generated = self.regenerate(study, language)

            if generated is not None:
                self.regenerated_diplomas_counter += 1

    def get_study_diploma_languages(self, study: Study) -> QuerySet:
        return DiplomaTemplate.objects.filter(
            course=study.course,
            homework_accepted=study.homework_accepted,
            language__in=self.student.diploma_languages,
        ).values_list('language', flat=True)

    def notify(self) -> None:
        send_mail.delay(
            to=self.student.email,
            template_id='diplomas_regenerated',
            disable_antispam=True,
        )

    def regenerate(self, study: Study, language: str) -> Diploma | None:
        with contextlib.suppress(DiplomaTemplate.DoesNotExist):  # we have manually generated diplomas
            return DiplomaGenerator(
                student=self.student,
                course=study.course,
                language=cast(Language, language),
            )()
