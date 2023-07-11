from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.db.models import QuerySet

from orders.models import Order

if TYPE_CHECKING:
    from users.models import Student


@dataclass
class TagMechanism(metaclass=ABCMeta):
    """Base tag setter class. All tags in the tag pipeline should be inherited from it"""

    user: "Student"

    def __call__(self) -> list[str]:
        """If tags may be applied to the given user -- return list of them"""
        if self.should_be_applied(self.user):
            return self.get_tags_to_append()
        return []

    @property
    @abstractmethod
    def tag_name(self) -> str:
        """Tag name to be recorded in the db"""

    @abstractmethod
    def should_be_applied(self, user: "Student") -> bool:
        """Check if tag should be applied

        use it to speedup tag pipeline
        """

    @abstractmethod
    def get_tags_to_append(self) -> list[str]:
        """Returns list tags which must be appended to user"""

    @staticmethod
    def get_user_orders(user: "Student") -> QuerySet[Order]:
        """All orders that user has"""
        return Order.objects.filter(user=user)


__all__ = [
    "TagMechanism",
]
