from typing import final, TYPE_CHECKING

from django.db.models import QuerySet

from users.tags.base import TagMechanism

if TYPE_CHECKING:
    from orders.models import Order
    from users.models import Student


@final
class PurchasedTag(TagMechanism):
    def get_tags_to_append(self) -> list[str]:
        paid_orders = self.get_paid_orders(self.student)
        return self.generate_tags_for_unpaid_orders(paid_orders)

    def get_paid_orders(self, student: "Student") -> QuerySet["Order"]:
        return self.get_student_orders(student).filter(paid__isnull=False, course__isnull=False)

    def generate_tags_for_unpaid_orders(self, paid_orders: QuerySet["Order"]) -> list[str]:
        slugs = paid_orders.values_list("course__slug", "course__group__slug")
        tags_to_append = []
        for course_slug, group_slug in slugs:
            tags_for_order = [f'{course_slug}__purchased)', f'{{group_slug}__purchased']
            tags_to_append.extend(tags_for_order)

        return tags_to_append

    @classmethod
    def get_tag_from_slug(cls, slug: str) -> str:
        return f"{slug}__purchased"
