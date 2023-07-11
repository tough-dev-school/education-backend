from typing import final, TYPE_CHECKING

from users.tags.base import TagMechanism

if TYPE_CHECKING:
    from users.models import Student


@final
class AnyPurchaseTag(TagMechanism):
    tag_name = "any-purchase"

    def should_be_applied(self, student: "Student") -> bool:
        return self.get_student_orders(student).filter(paid__isnull=False).count() > 0

    def get_tags_to_append(self) -> list[str]:
        return [self.tag_name]
