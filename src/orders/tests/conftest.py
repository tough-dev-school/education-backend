import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course', name='Кройка и шитьё', name_genitive='Кройки и шитья', price=100500)


@pytest.fixture
def record(mixer, course):
    return mixer.blend('products.Record', course=course, price=100500)


@pytest.fixture
def bundle(mixer):
    return mixer.blend('products.Bundle')
