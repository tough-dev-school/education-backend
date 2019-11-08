import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def tinkoff_credentials(settings):
    settings.TINKOFF_TERMINAL_KEY = 'testDEMO'
    settings.TINKOFF_TERMINAL_PASSWORD = 'Dfsfh56dgKl'
