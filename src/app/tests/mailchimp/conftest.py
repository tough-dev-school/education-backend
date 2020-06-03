import pytest
import requests_mock

from app.integrations.mailchimp import AppMailchimp

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_chimp_credentials(settings):
    settings.MAILCHIMP_API_KEY = 'key-us05'
    settings.MAILCHIMP_CONTACT_LIST_ID = '123cba'


@pytest.fixture
def mailchimp():
    client = AppMailchimp()

    with requests_mock.Mocker() as http_mock:
        client.http_mock = http_mock
        yield client


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', email='test@e.mail', first_name='Rulon', last_name='Oboev')
