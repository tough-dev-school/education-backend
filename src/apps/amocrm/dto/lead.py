from dataclasses import dataclass
from typing import TYPE_CHECKING

from apps.amocrm.client import http
from apps.orders.models import Order

if TYPE_CHECKING:
    from apps.amocrm.ids import STATUSES_NAMES


@dataclass
class AmoCRMLead:
    order: Order

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
