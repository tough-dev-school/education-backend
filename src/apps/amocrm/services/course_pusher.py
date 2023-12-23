from dataclasses import dataclass

from apps.amocrm.dto import AmoCRMProductDTO
from apps.amocrm.models import AmoCRMCourse
from apps.products.models import Course
from core.services import BaseService


@dataclass
class AmoCRMCoursePusher(BaseService):
    """Push given course to amocrm"""

    course: Course

    def act(self) -> None:
        if not hasattr(self.course, "amocrm_course"):
            self.create_course(course=self.course)
        else:
            self.update_course(course=self.course)

    def create_course(self, course: Course) -> None:
        course_id = AmoCRMProductDTO(course=course).create()
        AmoCRMCourse.objects.create(
            course=course,
            amocrm_id=course_id,
        )

    def update_course(self, course: Course) -> None:
        AmoCRMProductDTO(course=course).update()
