from http import HTTPStatus
from typing import TypedDict

from apps.amocrm.client import http
from apps.amocrm.definitions import AmoCRMTaskType


class AmoCRMTask(TypedDict):
    """Only fields that are used in the app are listed.

    All the available fields are listed in docs:
    https://www.amocrm.ru/developers/content/crm_platform/tasks-api#tasks-list
    """

    id: int
    task_type_id: AmoCRMTaskType
    is_completed: bool
    text: str


class AmoCRMLeadTaskDTO:
    """https://www.amocrm.ru/developers/content/crm_platform/tasks-api"""

    def get_tasks(self, lead_id: int, is_completed: bool | None = None) -> list[AmoCRMTask]:
        params = {
            "filter[entity_type]": "leads",
            "filter[entity_id]": lead_id,
            "order[created_at]": "desc",
        }

        if is_completed is not None:
            params["filter[is_completed]"] = 1 if is_completed else 0

        response_data = http.get(
            url="/api/v4/tasks",
            params=params,
            expected_status_codes=[HTTPStatus.OK, HTTPStatus.NO_CONTENT],
        )

        if not response_data:
            return []

        return [
            AmoCRMTask(
                id=task_data["id"],
                task_type_id=task_data["task_type_id"],
                is_completed=task_data["is_completed"],
                text=task_data["text"],
            )
            for task_data in response_data["_embedded"]["tasks"]
        ]

    def create_task(self, lead_id: int, task_type_id: AmoCRMTaskType, task_text: str, timestamp_complete_till: int, responsible_user_id: int) -> int:
        data = {
            "entity_type": "leads",
            "entity_id": lead_id,
            "task_type_id": task_type_id,
            "text": task_text,
            "complete_till": timestamp_complete_till,
            "responsible_user_id": responsible_user_id,
        }

        response_data = http.post(url="/api/v4/tasks", data=[data])

        return response_data["_embedded"]["tasks"][0]["id"]
