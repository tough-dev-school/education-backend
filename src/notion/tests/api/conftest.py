import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture(autouse=True)
def order(factory, course, api):
    return factory.order(
        user=api.user,
        item=course,
    )
