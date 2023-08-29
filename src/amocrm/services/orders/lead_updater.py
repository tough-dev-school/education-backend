from dataclasses import dataclass

from amocrm.cache.lead_b2c_pipeline_id import get_b2c_pipeline_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.client import AmoCRMClient
from app.services import BaseService
from orders.models import Order


@dataclass
class AmoCRMLeadUpdater(BaseService):
    """
    Updates amocrm_lead for given order
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> None:
        self.client.update_lead(
            lead_id=self.order.amocrm_lead.amocrm_id,  # type: ignore
            status_id=get_b2c_pipeline_status_id(status_name="first_contact"),
            pipeline_id=get_b2c_pipeline_id(),
            price=self.order.price,
            created_at=self.order.created,
        )
