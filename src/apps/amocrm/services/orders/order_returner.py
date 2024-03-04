from dataclasses import dataclass

from apps.amocrm.dto import AmoCRMLeadDTO, AmoCRMTransactionDTO
from apps.orders.models import Order
from core.services import BaseService


@dataclass
class AmoCRMOrderReturner(BaseService):
    """Updates amocrm_lead for given order and deletes transaction"""

    order: Order

    def act(self) -> None:
        if self.order.amocrm_transaction is None:  # order is not pushed to amocrm as purchased
            return

        AmoCRMLeadDTO(order=self.order).update(status="closed")
        AmoCRMTransactionDTO(order=self.order).delete()
        self.order.amocrm_transaction.delete()
