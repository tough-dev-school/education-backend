from typing import Type  # NOQA: I251

from apps.products.models.bundle import Bundle
from apps.products.models.course import Course
from apps.products.models.group import Group
from apps.products.models.record import Record

Product = Course
ProductType = Type[Course]

__all__ = [
    "Bundle",
    "Course",
    "Group",
    "Record",
    "Product",
    "ProductType",
]
