import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def question(mixer, course):
    return mixer.blend('homework.Question', course=course)
