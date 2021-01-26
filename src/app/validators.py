from typing import Optional

from rest_framework.serializers import *  # noqa


class Validator(Serializer):  # noqa
    """Validator is a DRF-serializer based validator for end-user data
    Use it to produce developer-friendly errors
    """
    @classmethod
    def do(cls, data: dict, context: Optional[dict] = None) -> bool:
        instance = cls(data=data, context=context)

        return instance.is_valid(raise_exception=True)
