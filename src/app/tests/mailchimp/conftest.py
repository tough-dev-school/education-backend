import pytest
import requests_mock

from app.integrations.mailchimp import AppMailchimp, MailchimpMember

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def set_mailchimp_credentials(settings):
    settings.MAILCHIMP_API_KEY = 'key-us05'
    settings.MAILCHIMP_CONTACT_LIST_ID = '123cba'


@pytest.fixture
def mailchimp():
    client = AppMailchimp()

    with requests_mock.Mocker() as http_mock:
        client.http_mock = http_mock
        yield client


@pytest.fixture
def mailchimp_member(user):
    return MailchimpMember.from_django_user(user)


@pytest.fixture
def post(mocker):
    return mocker.patch('app.integrations.mailchimp.http.MailchimpHTTP.post')


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', email='test@e.mail', first_name='Rulon', last_name='Oboev')
