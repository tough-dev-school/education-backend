from typing import Any

from rest_framework import serializers

from core.markdown import markdownify


class MarkdownField(serializers.ReadOnlyField):
    """A field to render markdown"""

    def to_representation(self, obj: str) -> str:
        return markdownify(obj)


class SoftField(serializers.ReadOnlyField):
    """
    Field that does not fail when underliying instance has no defined attribute.
    Usefull for annotated model attributes — sometimes they may be present, sometimes not.
    If attribute does not exist — returns None
    """

    def get_attribute(self, instance: Any) -> Any:
        try:
            return super().get_attribute(instance)

        except AttributeError:
            return
