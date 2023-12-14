from apps.amocrm.client import http
from httpx import codes as status_codes
from typing import TypedDict


class AmoCRMTask(TypedDict):
    """Only fields that are used in the app are listed.

    All the available fields are listed in docs:
    https://www.amocrm.ru/developers/content/crm_platform/tasks-api#tasks-list
    """

    id: int
    task_type_id: int
    is_completed: bool
    text: str


class AmoCRMTaskConnector:
    """https://www.amocrm.ru/developers/content/crm_platform/tasks-api"""

    def get_lead_tasks(self, lead_id: int) -> list[AmoCRMTask]:
        params = {
            "filter[entity_type]": "leads",
            "filter[entity_id]": lead_id,
            "order[created_at]": "desc",
        }

        response_data = http.get(
            url=f"/api/v4/tasks",
            params=params,
            expected_status_codes=[status_codes.OK, status_codes.NO_CONTENT],
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


    def create_lead_task(self, lead_id: int, task_type_id: int, task_text: str, timestamp_complete_till: int, responsible_user_id: int) -> int:
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
