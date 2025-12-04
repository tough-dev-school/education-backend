from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


@extend_schema_field(OpenApiTypes.BINARY)
class BinaryUploadField(serializers.FileField):
    """Used in API schema, to explitily mark file requests as binary"""


__all__ = [
    "BinaryUploadField",
]
