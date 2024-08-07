from typing import Any

from apps.products.models import Course, Group
from core.helpers import random_string
from core.test.factory import register


@register
def course(self: Any, slug: str | None = None, group: Group | None = None, **kwargs: dict[str, Any]) -> Course:
    return self.mixer.blend(
        "products.Course",
        slug=slug if slug is not None else random_string(49),
        group=group if group is not None else self.group(),
        **kwargs,
    )


@register
def group(self: Any, slug: str | None = None, **kwargs: dict[str, Any]) -> Group:
    return self.mixer.blend(
        "products.Group",
        slug=slug if slug is not None else random_string(49),
        **kwargs,
    )
