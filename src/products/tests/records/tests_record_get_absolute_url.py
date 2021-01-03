import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_main_website(settings):
    settings.FRONTEND_URL = 'https://test.mocked'


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', slug='tst-slug')


def test(mixer, course):
    record = mixer.blend('products.Record', course=course)

    assert record.get_absolute_url() == 'https://test.mocked/courses/tst-slug/'
