from markdownx.settings import MARKDOWNX_MARKDOWNIFY_FUNCTION
from rest_framework import serializers

from django.utils.module_loading import import_string


class MarkdownXField(serializers.ReadOnlyField):
    """A field to render markdown"""

    def to_representation(self, obj):
        markdownify = import_string(MARKDOWNX_MARKDOWNIFY_FUNCTION)
        return markdownify(obj)


class SoftField(serializers.ReadOnlyField):
    """
    Field that does not fail when underliying instance has no defined attribute.
    Usefull for annotated model attributes — sometimes they may be present, sometimes not.
    If attribute does not exist — returns None
    """

    def get_attribute(self, instance):
        try:
            return super().get_attribute(instance)

        except AttributeError:
            return
