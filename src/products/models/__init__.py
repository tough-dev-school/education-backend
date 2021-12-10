from typing import Type, Union

from products.models.bundle import Bundle
from products.models.course import Course
from products.models.group import Group
from products.models.record import Record

Product = Union[Course, Bundle, Record]
ProductType = Union[Type[Course], Type[Bundle], Type[Record]]

__all__ = [
    'Bundle',
    'Course',
    'Group',
    'Record',
    'Product',
    'ProductType',
]
