from typing import final, TYPE_CHECKING

from django.db.models import QuerySet

from users.tags.base import TagMechanism

if TYPE_CHECKING:
    from orders.models import Order
    from users.models import Student


@final
class StartedTag(TagMechanism):
    def get_tags_to_append(self) -> list[str]:
        unpaid_orders = self.get_unpaid_orders(self.student)
        return self.generate_tags_for_unpaid_orders(unpaid_orders)

    def get_unpaid_orders(self, student: "Student") -> QuerySet["Order"]:
        groups_purchased_by_student = self.get_student_orders(student).filter(paid__isnull=False, course__isnull=False).values_list("course__group").distinct()

        return self.get_student_orders(student).filter(paid__isnull=True, course__isnull=False).exclude(course__group__in=groups_purchased_by_student)

    def generate_tags_for_unpaid_orders(self, unpaid_orders: QuerySet["Order"]) -> list[str]:
        slugs = unpaid_orders.values_list("course__slug", "course__group__slug")
        tags_to_append = []
        for course_slug, group_slug in slugs:
            tags_for_order = [self.get_tag_from_slug(course_slug), self.get_tag_from_slug(group_slug)]
            tags_to_append.extend(tags_for_order)

        return tags_to_append

    @classmethod
    def get_tag_from_slug(cls, slug: str) -> str:
        return f"{slug}__started"
