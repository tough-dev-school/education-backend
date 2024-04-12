from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from apps.products.models import Course


@pytest.fixture
def course(factory) -> "Course":
    return factory.course()


@pytest.fixture
def another_course(factory) -> "Course":
    return factory.course()
