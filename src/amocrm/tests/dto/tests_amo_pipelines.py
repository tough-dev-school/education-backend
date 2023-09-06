import pytest

from amocrm.dto.pipelines import AmoCRMPipelines

pytestmark = [
    pytest.mark.django_db,
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
def test_get_pipelines_return_list_of_pipelines(get):
    got = AmoCRMPipelines.get()

    assert got == [
        dict(
            id=7028886,
            name="b2b",
            statuses=[
                dict(id=58962662, name="Переговоры"),
                dict(id=142, name="Успешно реализовано"),
                dict(id=143, name="Закрыто и не реализовано"),
            ],
        ),
        dict(
            id=7055602,
            name="individual",
            statuses=[
                dict(id=59144290, name="Неразобранное"),
                dict(id=59144298, name="подготовить индивидуальный план"),
            ],
        ),
    ]


@pytest.mark.usefixtures("_successful_response")
def test_get_pipelines_call_cached(get):
    AmoCRMPipelines.get()

    get.assert_called_once_with(url="/api/v4/leads/pipelines", cached=True)
