from typing import Any, TYPE_CHECKING

from core.helpers import random_string
from core.test.factory import register

if TYPE_CHECKING:
    from apps.products.models import Course
    from apps.products.models import Group


@register
def course(self: Any, slug: str | None = None, **kwargs: dict[str, Any]) -> "Course":
    slug = slug if slug else random_string(50)

    return self.mixer.blend("products.Course", slug=slug, **kwargs)


@register
def group(self: Any, slug: str | None = None, **kwargs: dict[str, Any]) -> "Group":
    slug = slug if slug else random_string(50)

    return self.mixer.blend("products.Group", slug=slug, **kwargs)
