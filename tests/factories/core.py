from typing import TYPE_CHECKING

from django.core.files.uploadedfile import SimpleUploadedFile

from core.test.factory import register


if TYPE_CHECKING:
    from core.test.factory import FixtureFactory


@register
def image(self: "FixtureFactory", name: str = "image.gif", content_type: str = "image/gif") -> SimpleUploadedFile:
    return SimpleUploadedFile(name=name, content=self.faker.image(), content_type=content_type)
