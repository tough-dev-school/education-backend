from typing import Type

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
    "Product",
    "ProductType",
    "Record",
]
