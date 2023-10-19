import os
from typing import Any
import uuid

from django.utils.deconstruct import deconstructible


@deconstructible
class RandomFileName:
    """Random filename generator

    Usage:

        from core.files import RandomFileName

        class MyModel(models.Model):
            image = models.ImageField(upload_to=RandomFileName('images/folder')
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def __call__(self, _: Any, filename: str) -> str:
        extension = os.path.splitext(filename)[1]

        return os.path.join(self.path, f"{uuid.uuid4()}{extension}")
