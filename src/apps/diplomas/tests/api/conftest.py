import pytest

from apps.diplomas.models import Languages

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.update(is_superuser=False)

    return api


@pytest.fixture
def course(factory):
    return factory.course(name="Выход из зоны комфорта", name_international="Comfort zone exit")


@pytest.fixture
def diploma(factory, course):
    return factory.diploma(language=Languages.EN, course=course)
