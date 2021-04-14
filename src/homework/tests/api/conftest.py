import pytest
from django.utils import timezone

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


@pytest.fixture
def question(mixer, course):
    return mixer.blend('homework.Question', course=course)


@pytest.fixture
def purchase(mixer, course, api):
    return mixer.blend('orders.Order', user=api.user, course=course, paid=timezone.now())
