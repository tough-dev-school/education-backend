import pytest

from django.core.cache import cache

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _cached_tokens():
    cache.set("amocrm_access_token", None)
    cache.set("amocrm_refresh_token", "so-refreshing")


@pytest.fixture
def mock_refresh(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.refresh_tokens")


@pytest.fixture
def _refreshed_tokens_response(post):
    post.return_value = {"token_type": "Bearer", "expires_in": 86400, "access_token": "so-accessible", "refresh_token": "even-more-refreshing"}


@pytest.mark.usefixtures("_refreshed_tokens_response", "_cached_tokens")
def test_calls_post_with_correct_params(amocrm_client, post):
    amocrm_client.refresh_tokens()

    post.assert_called_with(
        url="/oauth2/access_token",
        data={
            "client_id": "4815162342",
            "client_secret": "top-secret-007",
            "grant_type": "refresh_token",
            "code": "so-refreshing",
            "redirect_uri": "https://test-education.ru",
        },
    )


@pytest.mark.usefixtures("_refreshed_tokens_response", "_cached_tokens")
def test_update_cached_tokens(amocrm_client, post):
    amocrm_client.refresh_tokens()

    assert cache.get("amocrm_access_token") == "so-accessible"
    assert cache.get("amocrm_refresh_token") == "even-more-refreshing"


@pytest.mark.usefixtures("post", "_cached_tokens")
def test_calls_auto_refresh_if_no_token(mock_refresh, amocrm_client, user):
    amocrm_client.create_customer(user)

    mock_refresh.assert_called_once()


@pytest.mark.usefixtures("post", "_cached_tokens")
def test_do_not_call_if_has_access_token(mock_refresh, amocrm_client, user):
    cache.set("amocrm_access_token", "here-we-are")

    amocrm_client.create_customer(user)

    mock_refresh.assert_not_called()
