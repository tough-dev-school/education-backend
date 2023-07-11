from typing import final, Generator, TYPE_CHECKING

from django.db.models import QuerySet

from products.models import Course
from users.tags.base import TagMechanism

if TYPE_CHECKING:
    from users.models import Student


@final
class PurchasedTag(TagMechanism):
    def get_tags_to_append(self) -> list[str]:
        purchased_courses = self.get_purchased_courses(self.student)
        return [f"{slug}__purchased" for slug in self.generate_slugs(purchased_courses)]

    def get_purchased_courses(self, student: "Student") -> QuerySet[Course]:
        purchased_courses = self.get_student_orders(student).filter(paid__isnull=False).values_list("course_id")

        return Course.objects.filter(pk__in=purchased_courses)

    def generate_slugs(self, non_paid_courses: QuerySet[Course]) -> Generator[str, None, None]:
        for course in non_paid_courses:
            yield course.slug

            if course.group is not None:
                yield course.group.slug
