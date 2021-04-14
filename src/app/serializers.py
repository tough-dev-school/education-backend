from markdownx.utils import markdownify
from rest_framework import serializers


class MarkdownXField(serializers.Field):
    """A field to render markdown"""
    def to_representation(self, obj):
        return markdownify(obj)
