from dataclasses import dataclass

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.lead_b2c_pipeline_id import get_b2c_pipeline_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import STATUSES_NAMES
from amocrm.dto.base import AmoDTO
from orders.models import Order


@dataclass
class AmoCRMLead(AmoDTO):
    order: Order

    def create(self) -> int:
        """Create lead for given order and returns lead_id"""
        lead_id = self._create_lead()
        self._link_course_to_lead(lead_id=lead_id, course_id=self.order.course.amocrm_course.amocrm_id)
        self._update_lead(lead_id=lead_id, status="first_contact")  # update lead price, cuz the particular order price might be different from the course price
        return lead_id

    def update(self, status: STATUSES_NAMES) -> None:
        """Update lead for given order"""
        self._update_lead(lead_id=self.order.amocrm_lead.amocrm_id, status=status)  # type: ignore

    def _create_lead(self) -> int:
        """
        Create lead and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-complex-add
        """
        data = self._get_order_as_lead()
        data.update(
            {
                "_embedded": {"contacts": [{"id": self.order.user.amocrm_user.contact_id}]},
                "status_id": get_b2c_pipeline_status_id(status_name="first_contact"),
            }
        )

        response = self.http.post(
            url="/api/v4/leads/complex",
            data=[data],
        )

        return response[0]["id"]  # type: ignore

    def _update_lead(self, lead_id: int, status: STATUSES_NAMES) -> None:
        """
        Updates existing lead
        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-edit
        """
        data = self._get_order_as_lead()
        data.update(
            {
                "id": lead_id,
                "status_id": get_b2c_pipeline_status_id(status_name=status),
            }
        )

        self.http.patch(
            url="/api/v4/leads",
            data=[data],
        )

    def _link_course_to_lead(self, lead_id: int, course_id: int) -> None:
        """
        Link given customer to given contact
        https://www.amocrm.ru/developers/content/crm_platform/entity-links-api#links-link
        """
        self.http.post(
            url=f"/api/v4/leads/{lead_id}/link",
            data=[
                {
                    "to_entity_id": course_id,
                    "to_entity_type": "catalog_elements",
                    "metadata": {
                        "quantity": 1,  # only 1 course per order
                        "catalog_id": get_catalog_id(catalog_type="products"),
                    },
                },
            ],
        )

    def _get_order_as_lead(self) -> dict:
        return {
            "pipeline_id": get_b2c_pipeline_id(),
            "price": int(self.order.price),  # amocrm api requires field to be integer
            "created_at": int(self.order.created.timestamp()),  # amocrm api requires to send integer timestamp
        }
