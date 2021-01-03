import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course')


@pytest.fixture
def record(mixer):
    return mixer.blend('courses.Record')


@pytest.fixture
def bundle(mixer):
    return mixer.blend('courses.Bundle')
