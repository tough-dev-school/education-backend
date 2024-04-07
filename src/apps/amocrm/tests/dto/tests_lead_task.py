import pytest

from apps.amocrm import types
from apps.amocrm.dto import AmoCRMLeadTaskDTO


@pytest.fixture
def _successful_lead_tasks_response(get):
    get.return_value = {
        "_page": 1,
        "_links": {
            "self": {
                "href": "https://thelord.amocrm.ru/api/v4/tasks?filter%5Bentity_type%5D=leads&filter%5Bentity_id%5D=1781381&order%5Bcreated_at%5D=desc&page=1&limit=250"
            }
        },
        "_embedded": {
            "tasks": [
                {
                    "id": 894053,
                    "created_by": 0,
                    "updated_by": 0,
                    "created_at": 1702556336,
                    "updated_at": 1702556336,
                    "responsible_user_id": 10446146,
                    "group_id": 0,
                    "entity_id": 1781381,
                    "entity_type": "leads",
                    "duration": 0,
                    "is_completed": False,
                    "task_type_id": 1,
                    "text": "hi!",
                    "result": [],
                    "complete_till": 1702640934,
                    "account_id": 31456190,
                    "_links": {
                        "self": {
                            "href": "https://thelord.amocrm.ru/api/v4/tasks/894053?filter%5Bentity_type%5D=leads&filter%5Bentity_id%5D=1781381&order%5Bcreated_at%5D=desc&page=1&limit=250"
                        }
                    },
                },
            ]
        },
    }


@pytest.fixture
def _successful_lead_task_created_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://thelord.amocrm.ru/api/v4/tasks"}},
        "_embedded": {
            "tasks": [
                {
                    "id": 905769,
                    "request_id": "0",
                    "_links": {
                        "self": {
                            "href": "https://thelord.amocrm.ru/api/v4/tasks/905769",
                        }
                    },
                },
            ],
        },
    }


@pytest.fixture
def dto():
    return AmoCRMLeadTaskDTO()


@pytest.mark.usefixtures("_successful_lead_tasks_response")
def test_amo_crm_task_dto_return_amocrm_tasks(dto):
    got = dto.get(lead_id=1781381)

    assert got == [
        types.Task(
            id=894053,
            task_type_id=types.TaskType.CONTACT,
            is_completed=False,
            text="hi!",
        ),
    ]


@pytest.mark.usefixtures("_successful_lead_tasks_response")
def test_get_lead_tasks_call_amo_client_with_correct_params(dto, get):
    dto.get(lead_id=1781381)

    get.assert_called_once_with(
        url="/api/v4/tasks",
        expected_status_codes=[200, 204],  # NO_CONTENT - 204 is returned when there are no tasks matching the filter
        params={
            "filter[entity_type]": "leads",
            "filter[entity_id]": 1781381,
            "order[created_at]": "desc",
        },
    )


def test_get_lead_task_filtered_by_completed_call_amo_client_with_correct_params(dto, get):
    dto.get(lead_id=1781381, is_completed=True)

    get.assert_called_once_with(
        url="/api/v4/tasks",
        expected_status_codes=[200, 204],
        params={
            "filter[entity_type]": "leads",
            "filter[entity_id]": 1781381,
            "filter[is_completed]": 1,
            "order[created_at]": "desc",
        },
    )


def test_get_lead_tasks_return_empty_list_if_no_matching_tasks(dto, get):
    get.return_value = {}

    got = dto.get(lead_id=1781381)

    assert got == []


@pytest.mark.usefixtures("_successful_lead_task_created_response")
def test_create_lead_task_call_amo_client_with_correct_params(dto, post):
    got = dto.create(
        lead_id=1781381,
        task_type_id=types.TaskType.CONTACT,
        task_text="hi!",
        timestamp_complete_till=1702640934,
        responsible_user_id=10446146,
    )

    assert got == 905769
    post.assert_called_once_with(
        url="/api/v4/tasks",
        data=[
            {
                "entity_id": 1781381,
                "entity_type": "leads",
                "task_type_id": 1,
                "text": "hi!",
                "complete_till": 1702640934,
                "responsible_user_id": 10446146,
            },
        ],
    )
