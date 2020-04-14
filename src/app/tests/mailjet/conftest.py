import pytest

from app.integrations.mailjet import AppMailjet

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_mailjet_credentials(settings):
    settings.MAILJET_API_KEY = 'key'
    settings.MAILJET_SECRET_KEY = 'secret'
    settings.MAILJET_CONTACT_LIST_ID = 100500


@pytest.fixture
def mailjet():
    return AppMailjet()


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', email='test@e.mail', first_name='Rulon', last_name='Oboev')
