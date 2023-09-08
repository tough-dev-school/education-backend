import pytest

from respx import MockRouter

from app.integrations.dashamail import AppDashamail

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _mock_subscription_updater():  # override global mock to test dashamail
    return


@pytest.fixture(autouse=True)
def _set_dashamail_credentials(settings):
    settings.DASHAMAIL_API_KEY = "apikey"
    settings.DASHAMAIL_LIST_ID = "1"


@pytest.fixture
def dashamail(respx_mock: MockRouter):
    client = AppDashamail()
    client.respx_mock = respx_mock  # type: ignore
    return client


@pytest.fixture
def successful_response_json():
    return {
        "response": {
            "msg": {
                "err_code": 0,
                "text": "error",
                "type": "message",
            },
            "data": {},
        },
    }


@pytest.fixture
def fail_response_json():
    return {
        "response": {
            "msg": {
                "err_code": 4,
                "text": "error",
                "type": "message",
            },
            "data": {},
        },
    }


@pytest.fixture
def post(mocker, successful_response_json):
    return mocker.patch("app.integrations.dashamail.http.DashamailHTTP.post", return_value=successful_response_json)


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", email="test@e.mail", first_name="Rulon", last_name="Oboev")
