import pytest

from django.core.cache import cache

from amocrm.client import AmoCRMClient


@pytest.fixture(autouse=True)
def _cached_tokens():
    cache.set("amocrm_access_token", "token")
    cache.set("amocrm_refresh_token", "refresh-token")


@pytest.fixture
def amocrm_client() -> AmoCRMClient:
    return AmoCRMClient()


@pytest.fixture
def get(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.get")
