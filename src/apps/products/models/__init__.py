from typing import Type

from apps.products.models.bundle import LegacyBundle
from apps.products.models.course import Course
from apps.products.models.group import Group
from apps.products.models.record import LegacyRecord

Product = Course
ProductType = Type[Course]

__all__ = [
    "Course",
    "Group",
    "LegacyBundle",
    "LegacyRecord",
    "Product",
    "ProductType",
]
