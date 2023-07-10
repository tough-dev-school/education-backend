from typing import final

from users.tags.base import TagSetterMechanism


@final
class AnyPurchaseTag(TagSetterMechanism):
    tag_name = "any-purchase"

    def should_be_applied(self) -> bool:
        return self.orders.filter(paid__isnull=False).count() > 0

    def apply(self) -> None:
        self.user.apply_tag(self.tag_name)
