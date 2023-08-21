from dataclasses import dataclass
from typing import Callable

from django.db.transaction import atomic

from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderTransactionDeleterException(AmoCRMServiceException):
    """Raises when it's impossible to delete customer's transaction"""


@dataclass
class AmoCRMOrderTransactionDeleter(BaseService):
    """
    Deletes customer's transaction for given order if it's unpaid
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    @atomic
    def act(self) -> None:
        self.client.delete_transaction(
            transaction_id=self.order.amocrm_transaction.amocrm_id,
        )
        self.order.amocrm_transaction.delete()

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_transaction_exist,
            self.validate_amocrm_customer_exist,
            self.validate_order_is_unpaid,
        ]

    def validate_transaction_exist(self) -> None:
        if not hasattr(self.order, "amocrm_transaction"):
            raise AmoCRMOrderTransactionDeleterException("Transaction doesnt exist")

    def validate_amocrm_customer_exist(self) -> None:
        if not hasattr(self.order.user, "amocrm_user"):
            raise AmoCRMOrderTransactionDeleterException("AmoCRM customer for order's user doesn't exist")

    def validate_order_is_unpaid(self) -> None:
        if self.order.unpaid is None:
            raise AmoCRMOrderTransactionDeleterException("Order must be unpaid")
