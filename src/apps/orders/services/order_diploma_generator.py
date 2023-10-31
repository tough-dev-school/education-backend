from dataclasses import dataclass

from django.utils.functional import cached_property

from apps.diplomas.models import DiplomaTemplate
from apps.diplomas.tasks import generate_diploma
from apps.orders.models import Order
from apps.products.models import Course
from apps.studying.models import Study
from apps.users.models import User
from core.services import BaseService


@dataclass
class OrderDiplomaGenerator(BaseService):
    order: Order

    def act(self) -> None:
        for language in self.get_available_languages():
            generate_diploma.delay(
                student_id=self.student.id,
                course_id=self.course.id,
                language=language,
            )

    @cached_property
    def study(self) -> Study:
        return self.order.study

    @cached_property
    def student(self) -> User:
        return self.study.student

    @cached_property
    def course(self) -> Course:
        return self.study.course

    def get_available_languages(self) -> list[str]:
        return [
            template.language
            for template in DiplomaTemplate.objects.filter(
                course=self.course,
                homework_accepted=self.study.homework_accepted,
                language__in=self.student.diploma_languages,
            )
        ]
