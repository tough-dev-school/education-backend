from dataclasses import dataclass

from amocrm.dto import AmoCRMLead
from amocrm.dto import AmoCRMTransaction
from app.services import BaseService
from orders.models import Order


@dataclass
class AmoCRMOrderReturner(BaseService):
    """
    Updates amocrm_lead for given order and deletes transaction
    """

    order: Order

    def act(self) -> None:
        AmoCRMLead(order=self.order).update(status="closed")
        AmoCRMTransaction(order=self.order).delete()
        self.order.amocrm_transaction.delete()  # type: ignore
