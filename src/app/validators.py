from rest_framework.serializers import *  # noqa


class Validator(Serializer):  # noqa
    """Validator is a DRF-serializer based validator for end-user data
    Use it to produce developer-friendly errors
    """
    @classmethod
    def do(cls, data: dict) -> bool:
        instance = cls(data=data)

        return instance.is_valid(raise_exception=True)
