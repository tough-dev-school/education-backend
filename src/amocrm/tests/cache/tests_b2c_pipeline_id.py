import pytest

from django.core.cache import cache

from amocrm.cache.lead_b2c_pipeline_id import get_b2c_pipeline_id
from amocrm.exceptions import AmoCRMCacheException
from amocrm.types import AmoCRMPipeline
from amocrm.types import AmoCRMPipelineStatus

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def b2c_pipeline():
    return AmoCRMPipeline(id=333, name="b2c", statuses=[AmoCRMPipelineStatus(id=5, name="statusss")])


@pytest.fixture
def pipelines(b2c_pipeline):
    return [b2c_pipeline, AmoCRMPipeline(id=111, name="individual", statuses=[AmoCRMPipelineStatus(id=10, name="hm status")])]


@pytest.fixture(autouse=True)
def mock_get_pipelines(mocker, pipelines):
    return mocker.patch("amocrm.client.AmoCRMClient.get_pipelines", return_value=pipelines)


def test_return_pipeline_if_in_cache(b2c_pipeline, mock_get_pipelines):
    cache.set("amocrm_b2c_pipeline_id", b2c_pipeline.id)

    got = get_b2c_pipeline_id()

    assert got == b2c_pipeline.id
    mock_get_pipelines.assert_not_called()


def test_return_pipeline_from_response_if_not_in_cache(b2c_pipeline, mock_get_pipelines):
    cache.clear()

    got = get_b2c_pipeline_id()
    assert got == b2c_pipeline.id
    assert cache.get("amocrm_b2c_pipeline_id") == b2c_pipeline.id
    mock_get_pipelines.assert_called_once()


def test_fail_if_not_in_cache_and_not_in_response(mock_get_pipelines):
    cache.clear()
    mock_get_pipelines.return_value = [AmoCRMPipeline(id=111, name="individual", statuses=[AmoCRMPipelineStatus(id=10, name="hm status")])]

    with pytest.raises(AmoCRMCacheException):
        get_b2c_pipeline_id()
