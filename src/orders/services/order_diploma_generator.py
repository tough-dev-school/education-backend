from dataclasses import dataclass
from django.utils.functional import cached_property

from diplomas.models import DiplomaTemplate
from diplomas.tasks import generate_diploma
from orders.models import Order
from products.models import Course
from studying.models import Study
from users.models import User


@dataclass
class OrderDiplomaGenerator:
    order: Order

    def __call__(self):
        for language in self.get_available_languages():
            if self.order_is_suitable_for_diploma_generation(language=language):
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
            )
        ]

    def order_is_suitable_for_diploma_generation(self, language) -> bool:
        return self.student.get_printable_name(language=language) is not None
