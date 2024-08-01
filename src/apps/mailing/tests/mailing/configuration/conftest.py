import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def configuration(course, mixer):
    return mixer.blend("mailing.EmailConfiguration", course=course)


@pytest.fixture
def another_configuration(another_course, mixer):
    return mixer.blend("mailing.EmailConfiguration", course=another_course)
