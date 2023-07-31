import pytest

from django.core.cache import cache

from amocrm.services.token_manager import AmoCRMTokenManager

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def manager():
    return AmoCRMTokenManager()


@pytest.fixture
def mock_response():
    class MockResponse:
        status_code = 200

        def json(self):
            return {"token_type": "Bearer", "expires_in": 86400, "access_token": "so-accessible", "refresh_token": "even-more-refreshing"}

    return MockResponse()


@pytest.fixture
def post(mocker, mock_response):
    return mocker.patch("httpx.Client.post", return_value=mock_response)


def test_calls_post_with_correct_params_when_no_access_token(manager, post):
    cache.set("amocrm_access_token", None)
    cache.set("amocrm_refresh_token", "so-refreshing")

    manager()

    post.assert_called_with(
        url="https://test.amocrm.ru/oauth2/access_token",
        data={
            "client_id": "4815162342",
            "client_secret": "top-secret-007",
            "grant_type": "refresh_token",
            "code": "so-refreshing",
            "redirect_uri": "https://test-education.ru",
        },
    )


def test_calls_post_with_correct_params_when_no_refresh_token(manager, post):
    cache.set("amocrm_access_token", None)
    cache.set("amocrm_refresh_token", None)

    manager()

    post.assert_called_with(
        url="https://test.amocrm.ru/oauth2/access_token",
        data={
            "client_id": "4815162342",
            "client_secret": "top-secret-007",
            "grant_type": "authorization_code",
            "code": "1337yep",
            "redirect_uri": "https://test-education.ru",
        },
    )


def test_update_cached_tokens(manager, post):
    cache.set("amocrm_access_token", None)
    cache.set("amocrm_refresh_token", "so-refreshing")

    manager()

    assert cache.get("amocrm_access_token") == "so-accessible"
    assert cache.get("amocrm_refresh_token") == "even-more-refreshing"
