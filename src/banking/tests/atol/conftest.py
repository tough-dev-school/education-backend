import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _configure_atol(settings):
    settings.ATOL_LOGIN = 'zer0cool'
    settings.ATOL_PASSWORD = 'love'
