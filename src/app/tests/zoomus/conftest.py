import pytest
import requests_mock

from app.integrations.zoomus.client import ZoomusClient

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _set_api_key(settings):
    settings.ZOOMUS_API_KEY = 'k3y'
    settings.ZOOMUS_API_SECRET = 's3cr3t'


@pytest.fixture
def client():
    client = ZoomusClient()

    with requests_mock.Mocker() as http_mock:
        client.http_mock = http_mock
        yield client


@pytest.fixture
def user(mixer):
    return mixer.blend('users.User', first_name='Авраам', last_name='Пейзенгольц', email='abrakham@mail.ru')
