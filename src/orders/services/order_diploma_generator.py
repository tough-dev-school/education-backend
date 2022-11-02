from dataclasses import dataclass
from django.utils.functional import cached_property

from diplomas.models import DiplomaTemplate
from diplomas.tasks import generate_diploma
from orders.models import Order
from products.models import Course
from users.models import User


@dataclass
class OrderDiplomaGenerator:
    order: Order

    def __call__(self):
        for language in self.get_available_languages():
            generate_diploma.delay(
                student_id=self.student.id,
                course_id=self.course.id,
                language=language,
            )

    @cached_property
    def student(self) -> User:
        return self.order.study.student

    @cached_property
    def course(self) -> Course:
        return self.order.study.course

    def get_available_languages(self) -> list[str]:
        return [
            template.language
            for template in DiplomaTemplate.objects.filter(
                course=self.course,
                language__in=self.student.diploma_languages,
            )
        ]
