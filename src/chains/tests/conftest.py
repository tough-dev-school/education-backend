import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def study(mixer, course, user):
    return mixer.blend('studying.Study', course=course, user=user)
