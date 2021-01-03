import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_main_website(settings):
    settings.FRONTEND_URL = 'https://test.mocked'


def test(mixer):
    course = mixer.blend('courses.Course', slug='tst-slug')

    assert course.get_absolute_url() == 'https://test.mocked/courses/tst-slug/'
