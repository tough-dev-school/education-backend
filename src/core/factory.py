from typing import TYPE_CHECKING

from faker import Faker

from django.core.files.uploadedfile import SimpleUploadedFile

from core.test.factory import register

faker = Faker()

if TYPE_CHECKING:
    from core.test.factory import FixtureFactory


@register
def image(self: "FixtureFactory", name: str = "image.gif", content_type: str = "image/gif") -> SimpleUploadedFile:
    return SimpleUploadedFile(name=name, content=faker.image(), content_type=content_type)
