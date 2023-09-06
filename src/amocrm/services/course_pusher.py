from dataclasses import dataclass

from amocrm.dto import AmoCRMProduct
from amocrm.models import AmoCRMCourse
from app.services import BaseService
from products.models import Course


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
        course_id = AmoCRMProduct(course=course).create()
        AmoCRMCourse.objects.create(
            course=course,
            amocrm_id=course_id,
        )

    def update_course(self, course: Course) -> None:
        AmoCRMProduct(course=course).update()
