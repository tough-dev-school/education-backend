from typing import final

from users.tags.base import TagSetterMechanism


@final
class AnyPurchaseTag(TagSetterMechanism):
    tag_name = "any-purchase"

    def should_be_applied(self) -> bool:
        has_paid_order = self.orders.filter(paid__isnull=False).count() > 0
        already_has_tag = self.tag_name in self.tags
        return has_paid_order and not already_has_tag

    def apply(self) -> None:
        self.user.apply_tag(self.tag_name)
