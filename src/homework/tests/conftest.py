import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _enable_homework_permissions_checking(settings):
    settings.DISABLE_HOMEWORK_PERMISSIONS_CHECKING = False
