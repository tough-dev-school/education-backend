from http import HTTPStatus

from apps.amocrm import types
from apps.amocrm.client import http


class AmoCRMLeadTaskDTO:
    """https://www.amocrm.ru/developers/content/crm_platform/tasks-api"""

    def get(self, lead_id: int, is_completed: bool | None = None) -> list[types.Task]:
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
            types.Task(
                id=task_data["id"],
                task_type_id=task_data["task_type_id"],
                is_completed=task_data["is_completed"],
                text=task_data["text"],
            )
            for task_data in response_data["_embedded"]["tasks"]
        ]

    def create(self, lead_id: int, task_type_id: types.TaskType, task_text: str, timestamp_complete_till: int, responsible_user_id: int) -> int:
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
