from typing import cast

from dataclasses import dataclass
from django.db.models import QuerySet

from app.types import Language
from diplomas.models import Diploma
from diplomas.services.diploma_generator import DiplomaGenerator
from mailing.tasks import send_mail
from users.models import User


@dataclass
class DiplomaRegenerator:
    student: User

    def __call__(self) -> None:
        if self.diplomas.count():
            regenerated_diplomas_count = self.regenerate_diplomas()

            if regenerated_diplomas_count > 0:
                self.notify()

    def regenerate_diplomas(self) -> int:
        count = 0
        for diploma in self.diplomas.iterator():
            generated = self.regenerate(diploma)

            if generated is not None:
                count += 1

        return count

    def notify(self) -> None:
        send_mail.delay(
            to=self.student.email,
            template_id='diplomas_regenerated',
            disable_antispam=True,
        )

    @property
    def diplomas(self) -> QuerySet[Diploma]:
        return (
            Diploma.objects.filter(study__student=self.student)
            .filter_with_template()  # some diplomas have no template, can't regenerate them
            .select_related('study')
        )

    def regenerate(self, diploma: Diploma) -> Diploma:
        return DiplomaGenerator(
            student=diploma.study.student,
            course=diploma.study.course,
            language=cast(Language, diploma.language),
        )()
