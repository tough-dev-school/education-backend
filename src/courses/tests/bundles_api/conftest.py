import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def bundle(mixer):
    return mixer.blend('courses.Bundle', slug='pinetree-tickets', name='Флаг и билет на ёлку')
