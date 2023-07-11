from typing import Type, TYPE_CHECKING

from django.conf import settings
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from users.models import Student
    from users.tags.base import TagMechanism


def apply_tags(student: "Student") -> None:
    """Apply configured tag pipeline to the student"""
    pipeline: list[Type["TagMechanism"]] = [import_string(tag_cls) for tag_cls in settings.TAG_PIPELINE]
    new_tags: set[str] = set()

    for tag_class in pipeline:
        new_tags.update(tag_class(student=student)())

    student.tags = list(new_tags)
    student.save()


__all__ = ["apply_tags"]
