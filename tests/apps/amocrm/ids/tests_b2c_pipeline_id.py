import pytest

from apps.amocrm import types
from apps.amocrm.exceptions import AmoCRMCacheException
from apps.amocrm.ids import b2c_pipeline_id, b2c_pipeline_status_id


@pytest.fixture
def unsorted_status():
    return types.PipelineStatus(id=5, name="Неразобранное")


@pytest.fixture
def b2c_pipeline(unsorted_status):
    return types.Pipeline(id=333, name="b2c", statuses=[unsorted_status])


@pytest.fixture
def pipelines(b2c_pipeline):
    return [
        b2c_pipeline,
        types.Pipeline(id=111, name="individual", statuses=[types.PipelineStatus(id=10, name="hm status")]),
    ]


@pytest.fixture(autouse=True)
def mock_get_pipelines(mocker, pipelines):
    return mocker.patch("apps.amocrm.dto.pipelines.AmoCRMPipelinesDTO.get", return_value=pipelines)


def test_return_pipeline_id(b2c_pipeline):
    got = b2c_pipeline_id()

    assert got == b2c_pipeline.id


def test_return_pipeline_status_id(unsorted_status):
    got = b2c_pipeline_status_id(status_name="unsorted")

    assert got == unsorted_status.id


def test_fail_if_no_such_pipeline(mock_get_pipelines):
    mock_get_pipelines.return_value = [
        types.Pipeline(id=111, name="individual", statuses=[types.PipelineStatus(id=10, name="hm status")]),
    ]

    with pytest.raises(AmoCRMCacheException):
        b2c_pipeline_id()


def test_fail_if_no_such_status():
    with pytest.raises(AmoCRMCacheException):
        b2c_pipeline_status_id(status_name="closed")
