import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from products.models import Bundle
    from products.models import Course
    from products.models import Record


@pytest.fixture
def course(factory) -> "Course":
    return factory.course()


@pytest.fixture
def bundle(factory) -> "Bundle":
    return factory.bundle()


@pytest.fixture
def record(factory) -> "Record":
    return factory.record()


@pytest.fixture
def another_course(factory) -> "Course":
    return factory.course()


@pytest.fixture
def another_record(factory) -> "Record":
    return factory.record()
