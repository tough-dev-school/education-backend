from abc import ABCMeta
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field

from django.db.models import QuerySet

from orders.models import Order
from users.models import User
from users.tags.metadata import TagSetterMetadata


@dataclass
class TagSetterMechanism(metaclass=ABCMeta):
    """Base tag setter class. All tags in the tag pipeline should be inherited from it"""

    user: User
    metadata: TagSetterMetadata

    incompatible_tags: list[str] = field(default_factory=list)

    def __call__(self) -> None:
        """If tag in compatible with already applied tags and may be applied to the given user -- apply it"""
        if self.no_incompatible_tags_already_applied() and self.should_be_applied():
            self.apply()
            self.metadata.applied_tags.append(self.name)
        else:
            self.execute_if_not_applied()

    @property
    @abstractmethod
    def tag_name(self) -> str:
        """Tag name to be recorded in the db"""

    @abstractmethod
    def should_be_applied(self) -> bool:
        """Check if tag should be applied

        use it to speedup tag pipeline
        """

    @abstractmethod
    def apply(self) -> None:
        """Actualy applies the tag in subclass"""

    def execute_if_not_applied(self) -> None:  # NOQA: B027
        """Some optional actions to execute if tag isn't applied"""

    @property
    def tags(self) -> list[str]:
        """Tags that user has"""
        return self.user.tags

    @property
    def orders(self) -> QuerySet[Order]:
        """All orders that user has"""
        return Order.objects.filter(user=self.user)  # type: ignore

    @property
    def name(self) -> str:
        """Name of the tag"""
        return self.__class__.__name__

    def no_incompatible_tags_already_applied(self) -> bool:
        return not any(incompatible_tag in self.metadata.applied_tags for incompatible_tag in self.incompatible_tags)


__all__ = [
    "TagSetterMechanism",
]
