import pytest
import requests_mock

from app.integrations.clickmeeting import ClickMeetingClient

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_api_key(settings):
    settings.CLICKMEETING_API_KEY = 's3c3r37'


@pytest.fixture
def client():
    client = ClickMeetingClient()

    with requests_mock.Mocker() as http_mock:
        client.http_mock = http_mock
        yield client
