from dataclasses import dataclass
from http import HTTPStatus
from typing import TYPE_CHECKING, TypedDict

from django.utils.functional import cached_property

from apps.amocrm.client import http
from apps.amocrm.exceptions import AmoCRMException
from apps.orders.models import Order

if TYPE_CHECKING:
    from apps.amocrm.ids import STATUSES_NAMES


class AmoCRMLeadTask(TypedDict):
    """Only fields that are used in the app are listed.

    All the available fields are listed in docs:
    https://www.amocrm.ru/developers/content/crm_platform/tasks-api#tasks-list
    """

    id: int
    task_type_id: int
    is_completed: bool
    text: str


@dataclass
class AmoCRMLead:
    order: Order

    @cached_property
    def lead_id(self) -> int:
        """Be sure that the `self.order` is linked with with amocrm lead, otherwise AmoCRMException will be raised."""
        if not self.order.amocrm_lead:
            raise AmoCRMException("The order has to be linked with amocrm lead")

        return self.order.amocrm_lead.amocrm_id

    def create(self) -> int:
        """Create lead for given order and returns lead_id"""
        lead_id = self._create_lead()
        self._link_course_to_lead(lead_id=lead_id, course_id=self.order.course.amocrm_course.amocrm_id)
        self._set_price_from_order(lead_id=lead_id)  # update lead price, cuz the particular order price might be different from the course price
        return lead_id

    def update(self, status: "STATUSES_NAMES | None" = None) -> None:
        """
        Updates existing lead for given order
        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-edit
        """

        from apps.amocrm.ids import b2c_pipeline_status_id

        data = self._get_order_as_lead()
        data.update({"id": self.order.amocrm_lead.amocrm_id})  # type: ignore
        if status is not None:
            data.update({"status_id": b2c_pipeline_status_id(status_name=status)})

        http.patch(
            url="/api/v4/leads",
            data=[data],
        )

    def _create_lead(self) -> int:
        """
        Create lead and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-complex-add
        """
        from apps.amocrm.ids import b2c_pipeline_status_id

        data = self._get_order_as_lead()
        data.update(
            {
                "_embedded": {"contacts": [{"id": self.order.user.amocrm_user.contact_id}]},
                "status_id": b2c_pipeline_status_id(status_name="first_contact"),
            }
        )

        response = http.post(
            url="/api/v4/leads/complex",
            data=[data],
        )

        return response[0]["id"]  # type: ignore

    def _set_price_from_order(self, lead_id: int) -> None:
        """Update lead's price to match order's price"""
        data = self._get_order_as_lead()
        data.update({"id": lead_id})

        http.patch(
            url="/api/v4/leads",
            data=[data],
        )

    def _link_course_to_lead(self, lead_id: int, course_id: int) -> None:
        """
        Link given customer to given contact
        https://www.amocrm.ru/developers/content/crm_platform/entity-links-api#links-link
        """
        from apps.amocrm.ids import products_catalog_id

        http.post(
            url=f"/api/v4/leads/{lead_id}/link",
            data=[
                {
                    "to_entity_id": course_id,
                    "to_entity_type": "catalog_elements",
                    "metadata": {
                        "quantity": 1,  # only 1 course per order
                        "catalog_id": products_catalog_id(),
                    },
                },
            ],
        )

    def _get_order_as_lead(self) -> dict:
        from apps.amocrm.ids import b2c_pipeline_id

        return {
            "pipeline_id": b2c_pipeline_id(),
            "price": int(self.order.price),  # amocrm api requires field to be integer
            "created_at": int(self.order.created.timestamp()),  # amocrm api requires to send integer timestamp
        }

    def get_tasks(self) -> list[AmoCRMLeadTask]:
        """https://www.amocrm.ru/developers/content/crm_platform/tasks-api#task-detail"""

        params = {
            "filter[entity_type]": "leads",
            "filter[entity_id]": self.lead_id,
            "order[created_at]": "desc",
        }

        response_data = http.get(
            url="/api/v4/tasks",
            params=params,
            expected_status_codes=[HTTPStatus.OK, HTTPStatus.NO_CONTENT],
        )

        if not response_data:
            return []

        return [
            AmoCRMLeadTask(
                id=task_data["id"],
                task_type_id=task_data["task_type_id"],
                is_completed=task_data["is_completed"],
                text=task_data["text"],
            )
            for task_data in response_data["_embedded"]["tasks"]
        ]

    def create_task(self, task_type_id: int, task_text: str, timestamp_complete_till: int, responsible_user_id: int) -> int:
        """https://www.amocrm.ru/developers/content/crm_platform/tasks-api#tasks-add"""

        data = {
            "entity_type": "leads",
            "entity_id": self.lead_id,
            "task_type_id": task_type_id,
            "text": task_text,
            "complete_till": timestamp_complete_till,
            "responsible_user_id": responsible_user_id,
        }

        response_data = http.post(url="/api/v4/tasks", data=[data])

        return response_data["_embedded"]["tasks"][0]["id"]

    def create_note(self, service_name: str, note_text: str) -> int:
        """https://www.amocrm.ru/developers/content/crm_platform/events-and-notes#notes-common-info"""

        data = {
            "note_type": "service_message",
            "params": {
                "service": service_name,
                "text": note_text,
            },
        }

        response_data = http.post(url=f"/api/v4/leads/{self.lead_id}/notes", data=[data])

        return response_data["_embedded"]["notes"][0]["id"]
