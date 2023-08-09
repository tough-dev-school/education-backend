import pytest

from amocrm.types import AmoCRMPipeline
from amocrm.types import AmoCRMPipelineStatus

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(get):
    get.return_value = {
        "_total_items": 3,
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines"}},
        "_embedded": {
            "pipelines": [
                {
                    "id": 7028886,
                    "name": "b2b",
                    "sort": 1,
                    "is_main": True,
                    "is_unsorted_on": True,
                    "is_archive": False,
                    "account_id": 31182082,
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7028886"}},
                    "_embedded": {
                        "statuses": [
                            {
                                "id": 58962662,
                                "name": "Переговоры",
                                "sort": 30,
                                "is_editable": True,
                                "pipeline_id": 7028886,
                                "color": "#ffff99",
                                "type": 0,
                                "account_id": 31182082,
                                "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7028886/statuses/58962662"}},
                            },
                            {
                                "id": 142,
                                "name": "Успешно реализовано",
                                "sort": 10000,
                                "is_editable": False,
                                "pipeline_id": 7028886,
                                "color": "#CCFF66",
                                "type": 0,
                                "account_id": 31182082,
                                "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7028886/statuses/142"}},
                            },
                            {
                                "id": 143,
                                "name": "Закрыто и не реализовано",
                                "sort": 11000,
                                "is_editable": False,
                                "pipeline_id": 7028886,
                                "color": "#D5D8DB",
                                "type": 0,
                                "account_id": 31182082,
                                "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7028886/statuses/143"}},
                            },
                        ]
                    },
                },
                {
                    "id": 7055602,
                    "name": "individual",
                    "sort": 3,
                    "is_main": False,
                    "is_unsorted_on": True,
                    "is_archive": False,
                    "account_id": 31182082,
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7055602"}},
                    "_embedded": {
                        "statuses": [
                            {
                                "id": 59144290,
                                "name": "Неразобранное",
                                "sort": 10,
                                "is_editable": False,
                                "pipeline_id": 7055602,
                                "color": "#c1c1c1",
                                "type": 1,
                                "account_id": 31182082,
                                "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7055602/statuses/59144290"}},
                            },
                            {
                                "id": 59144298,
                                "name": "подготовить индивидуальный план",
                                "sort": 30,
                                "is_editable": True,
                                "pipeline_id": 7055602,
                                "color": "#ffff99",
                                "type": 0,
                                "account_id": 31182082,
                                "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/leads/pipelines/7055602/statuses/59144298"}},
                            },
                        ]
                    },
                },
            ]
        },
    }


@pytest.mark.usefixtures("_successful_response")
def test_get_pipelines(user, amocrm_client, get):
    got = amocrm_client.get_pipelines()

    assert got == [
        AmoCRMPipeline(
            id=7028886,
            name="b2b",
            statuses=[
                AmoCRMPipelineStatus(id=58962662, name="Переговоры"),
                AmoCRMPipelineStatus(id=142, name="Успешно реализовано"),
                AmoCRMPipelineStatus(id=143, name="Закрыто и не реализовано"),
            ],
        ),
        AmoCRMPipeline(
            id=7055602,
            name="individual",
            statuses=[
                AmoCRMPipelineStatus(id=59144290, name="Неразобранное"),
                AmoCRMPipelineStatus(id=59144298, name="подготовить индивидуальный план"),
            ],
        ),
    ]
    get.assert_called_once_with(url="/api/v4/leads/pipelines")
