from typing import final

from apps.users.tags.base import TagMechanism


@final
class AnyPurchaseTag(TagMechanism):
    @property
    def should_be_applied(self) -> bool:
        return self.get_student_orders(self.student).filter(paid__isnull=False, price__gt=0).count() > 0

    def get_tags_to_append(self) -> list[str]:
        return ["any-purchase"] if self.should_be_applied else []
