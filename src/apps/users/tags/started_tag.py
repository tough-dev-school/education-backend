from typing import final, Generator, TYPE_CHECKING

from django.db.models import QuerySet

from apps.products.models import Course
from apps.users.tags.base import TagMechanism

if TYPE_CHECKING:
    from apps.users.models import Student


@final
class StartedTag(TagMechanism):
    def get_tags_to_append(self) -> list[str]:
        non_paid_courses = self.get_non_paid_courses(self.student)
        return [f"{slug}__started" for slug in self.generate_slugs(non_paid_courses)]

    def get_non_paid_courses(self, student: "Student") -> QuerySet[Course]:
        orders = self.get_student_orders(student)
        paid_orders = orders.filter(paid__isnull=False)

        groups_with_purchased_courses = paid_orders.values_list("course__group")
        purchased_courses = set(paid_orders.values_list("course_id", flat=True))
        started_courses = set(orders.filter(paid__isnull=True).values_list("course_id", flat=True))

        return Course.objects.filter(pk__in=started_courses.difference(purchased_courses)).exclude(group__in=groups_with_purchased_courses)

    def generate_slugs(self, non_paid_courses: QuerySet[Course]) -> Generator[str, None, None]:
        for course in non_paid_courses:
            yield course.slug

            if course.group is not None:
                yield course.group.slug
