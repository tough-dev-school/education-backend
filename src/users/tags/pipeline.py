from typing import Type, TYPE_CHECKING

from django.conf import settings
from django.db.transaction import atomic
from django.utils.module_loading import import_string

from app.integrations.dashamail.helpers import subscribe_user_to_dashamail
from users.models import User
from users.tags.metadata import TagSetterMetadata

if TYPE_CHECKING:
    from users.tags.base import TagSetterMechanism


@atomic
def apply_tags(user: User) -> None:
    """Apply configured tag pipeline to the user"""
    metadata = TagSetterMetadata(user=user)  # single metadata object for all elements of the pipeline
    pipeline: list[Type["TagSetterMechanism"]] = [import_string(tag_cls) for tag_cls in settings.TAG_PIPELINE]

    for tag_class in pipeline:
        tag_class(user=user, metadata=metadata)()  # apply the tag

    subscribe_user_to_dashamail(user, tags=user.tags)


__all__ = ["apply_tags"]
