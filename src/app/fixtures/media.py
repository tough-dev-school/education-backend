import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.core.files.uploadedfile import SimpleUploadedFile

    from app.test.factory import FixtureFactory


@pytest.fixture
def image(factory: "FixtureFactory") -> "SimpleUploadedFile":
    return factory.image()
