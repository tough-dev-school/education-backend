from typing import final, TYPE_CHECKING

from django.db.models import Q
from django.db.models import QuerySet

from users.tags.base import TagMechanism

if TYPE_CHECKING:
    from orders.models import Order
    from users.models import Student


@final
class StartedTag(TagMechanism):
    def get_tags_to_append(self) -> list[str]:
        unpaid_orders = self.get_unpaid_orders(self.student)
        return self.generate_tags(unpaid_orders)

    def get_unpaid_orders(self, student: "Student") -> QuerySet["Order"]:
        groups_purchased_by_student = self.get_student_orders(student).filter(paid__isnull=False, course__isnull=False).values_list("course__group").distinct()
        courses_purchased_by_student = self.get_student_orders(student).filter(paid__isnull=False, course__isnull=False).values_list("course").distinct()

        return self.get_student_orders(student).filter(
            Q(paid__isnull=True) & Q(course__isnull=False) & ~Q(course__group__in=groups_purchased_by_student) & ~Q(course__in=courses_purchased_by_student)
        )

    def generate_tags(self, unpaid_orders: QuerySet["Order"]) -> list[str]:
        slugs = unpaid_orders.values_list("course__slug", "course__group__slug")
        tags_to_apply = []
        for course_slug, group_slug in slugs:
            tags_to_apply.append(f"{course_slug}__started")
            if group_slug is not None:
                tags_to_apply.append(f"{group_slug}__started")

        return tags_to_apply
