from dataclasses import dataclass

from amocrm.cache.lead_b2c_pipeline_id import get_b2c_pipeline_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.client import AmoCRMClient
from app.services import BaseService
from orders.models import Order


@dataclass
class AmoCRMOrderReturner(BaseService):
    """
    Updates amocrm_lead for given order and deletes transaction

    Returns amocrm_id for amocrm_lead
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> int:
        lead_amocrm_id = self.update_lead_status()
        self.delete_transaction()

        return lead_amocrm_id

    def update_lead_status(self) -> int:
        return self.client.update_lead(
            lead_id=self.order.amocrm_lead.amocrm_id,  # type: ignore
            status_id=get_b2c_pipeline_status_id(status_name="closed"),
            pipeline_id=get_b2c_pipeline_id(),
            price=self.order.price,
            created_at=self.order.created,
        )

    def delete_transaction(self) -> None:
        self.client.delete_transaction(transaction_id=self.order.amocrm_transaction.amocrm_id)  # type: ignore
        self.order.amocrm_transaction.delete()  # type: ignore
