from typing import cast

from dataclasses import dataclass
from django.db.models import QuerySet

from app.tasks import send_mail
from app.types import Language
from diplomas.models import Diploma
from diplomas.services import DiplomaGenerator
from users.models import User


@dataclass
class DiplomaRegenerator:
    student: User

    def __call__(self) -> None:
        if self.diplomas.count():
            self.regenerate_diplomas()
            self.notify()

    def regenerate_diplomas(self) -> None:
        for diploma in self.diplomas.iterator():
            self.regenerate(diploma)

    def notify(self) -> None:
        send_mail.delay(
            to=self.student.email,
            template_id='diplomas_regenerated',
            disable_antispam=True,
        )

    @property
    def diplomas(self) -> QuerySet[Diploma]:
        return Diploma.objects.filter(study__student=self.student).select_related('study')

    def regenerate(self, diploma: Diploma) -> Diploma:
        return DiplomaGenerator(
            student=diploma.study.student,
            course=diploma.study.course,
            language=cast(Language, diploma.language),
        )()
