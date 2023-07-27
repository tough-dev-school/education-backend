from typing import Any, TYPE_CHECKING

from app.helpers import random_string
from app.test.factory import register

if TYPE_CHECKING:
    from products.models import Course
    from products.models import Group


@register
def course(self: Any, slug: str | None = None, **kwargs: dict[str, Any]) -> "Course":
    slug = slug if slug else random_string(50)

    return self.mixer.blend("products.Course", slug=slug, **kwargs)


@register
def group(self: Any, slug: str | None = None, **kwargs: dict[str, Any]) -> "Group":
    slug = slug if slug else random_string(50)

    return self.mixer.blend("products.Group", slug=slug, **kwargs)
