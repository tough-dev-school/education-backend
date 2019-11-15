import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_main_website(settings):
    settings.ABSOLUTE_HOST = 'https://test.mocked'


@pytest.fixture
def course(mixer):
    return mixer.blend('courses.Course', slug='tst-slug')


def test(mixer, course):
    record = mixer.blend('courses.Record', course=course)

    assert record.get_absolute_url() == 'https://test.mocked/courses/tst-slug/'
