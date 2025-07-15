from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

from django.db.models import QuerySet

from apps.orders.models import Order
from apps.users.models import User


@dataclass
class TagMechanism(metaclass=ABCMeta):
    """Base tag mechanism class. All tags in the tag pipeline should be inherited from it"""

    student: User

    def __call__(self) -> list[str]:
        """If tags may be applied to the given student -- return list of them"""
        return self.get_tags_to_append()

    @abstractmethod
    def get_tags_to_append(self) -> list[str]:
        """Returns list of tags which must be appended to student"""

    @staticmethod
    def get_student_orders(student: "User") -> QuerySet[Order]:
        """All orders that student has"""
        return Order.objects.filter(user_id=student.pk)


__all__ = [
    "TagMechanism",
]
