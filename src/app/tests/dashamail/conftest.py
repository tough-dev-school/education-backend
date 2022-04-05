import pytest
import requests_mock

from app.integrations.dashamail import AppDashamail, DashamailMember

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_dashamail_credentials(settings):
    settings.DASHAMAIL_API_KEY = 'apikey'
    settings.DASHAMAIL_LIST_ID = '1'


@pytest.fixture
def dashamail():
    client = AppDashamail()

    with requests_mock.Mocker() as http_mock:
        client.http_mock = http_mock
        yield client


@pytest.fixture
def dashamail_member(user):
    member = DashamailMember.from_django_user(user)
    member.tags = ['test-tag', 'tag-test']
    return member


@pytest.fixture
def successful_response_json():
    return {
        'response': {
            'msg': {
                'err_code': 0,
                'text': 'error',
                'type': 'message',
            },
            'data': {},
        },
    }


@pytest.fixture
def post(mocker, successful_response_json):
    return mocker.patch('app.integrations.dashamail.http.DashamailHTTP.post', return_value=successful_response_json)


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', email='test@e.mail', first_name='Rulon', last_name='Oboev')
