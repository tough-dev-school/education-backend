from typing import TYPE_CHECKING, Type

from django.conf import settings
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from apps.users.models import User
    from apps.users.tags.base import TagMechanism


def generate_tags(user: "User") -> None:
    """Apply configured tag pipeline to the student"""
    pipeline: list[Type[TagMechanism]] = [import_string(tag_cls) for tag_cls in settings.TAG_PIPELINE]
    new_tags: set[str] = set()

    for tag_class in pipeline:
        new_tags.update(tag_class(student=user)())

    user.tags = list(new_tags)
    user.save(update_fields=["tags"])


__all__ = ["generate_tags"]
