from typing import Type  # NOQA: I251

from products.models.bundle import Bundle
from products.models.course import Course
from products.models.group import Group
from products.models.record import Record

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
