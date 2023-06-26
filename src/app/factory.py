from typing import Any

from faker import Faker

from django.core.files.uploadedfile import SimpleUploadedFile

from app.test.factory import register

faker = Faker()


@register
def image(self: Any, name: str = "image.gif", content_type: str = "image/gif") -> SimpleUploadedFile:
    return SimpleUploadedFile(name=name, content=faker.image(), content_type=content_type)
