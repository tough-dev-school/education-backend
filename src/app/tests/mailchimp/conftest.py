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
def post(mocker):
    return mocker.patch('app.integrations.mailchimp.http.MailchimpHTTP.post')


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', email='test@e.mail', first_name='Rulon', last_name='Oboev')


@pytest.fixture
def member_exists(mocker):
    return mocker.patch('app.integrations.mailchimp.AppMailchimp.member_exists')


@pytest.fixture
def member_is_always_new(member_exists):
    member_exists.return_value = False


@pytest.fixture
def subscribe(mocker):
    return mocker.patch('app.integrations.mailchimp.AppMailchimp._subscribe')
