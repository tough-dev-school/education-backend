from dataclasses import dataclass
from typing import Callable

from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.cache.lead_pipeline_id import get_pipeline_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderDeleterException(AmoCRMServiceException):
    """Raises when it's impossible to delete order in AmoCRM"""


@dataclass
class AmoCRMOrderDeleter(BaseService):
    """
    Updates amocrm_lead for given order and deletes transaction

    Returns amocrm_id for amocrm_lead
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> int:
        lead_amocrm_id = self.update_lead()
        self.delete_transaction()

        return lead_amocrm_id

    def update_lead(self) -> int:
        return self.client.update_lead(
            lead_id=self.order.amocrm_lead.amocrm_id,
            status_id=self.status_id,
            pipeline_id=self.pipeline_id,
            price=self.order.price,
            created_at=self.order.created,
        )

    def delete_transaction(self) -> None:
        self.client.delete_transaction(transaction_id=self.order.amocrm_transaction.amocrm_id)
        self.order.amocrm_transaction.delete()

    @property
    def pipeline_id(self) -> int:
        return get_pipeline_id(pipeline_name="b2c")

    @property
    def status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="closed")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_transaction_exist_if_paid,
        ]

    def validate_transaction_exist_if_paid(self) -> None:
        if self.order.amocrm_transaction is None:
            raise AmoCRMOrderDeleterException("Transaction for this unpaid order doesn't exists")
