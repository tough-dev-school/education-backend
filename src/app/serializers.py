from markdownx.utils import markdownify
from rest_framework import serializers


class MarkdownXField(serializers.Field):
    """A field to render markdown"""
    def to_representation(self, obj):
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
