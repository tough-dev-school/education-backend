import pytest

from diplomas.models import Languages

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions
    """
    api.user.is_superuser = False
    api.user.save()

    return api


@pytest.fixture
def diploma(factory):
    return factory.diploma(language=Languages.EN)
