from typing import final

from users.services import IsB2BEmailChecker
from users.tags.base import TagMechanism


@final
class B2BTag(TagMechanism):
    @property
    def should_be_applied(self) -> bool:
        return IsB2BEmailChecker(self.student.email)()

    def get_tags_to_append(self) -> list[str]:
        return ["b2b"] if self.should_be_applied else []
