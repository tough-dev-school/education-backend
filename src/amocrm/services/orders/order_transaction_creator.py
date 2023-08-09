from typing import Callable

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderTransaction
from amocrm.types import AmoCRMTransactionElement
from amocrm.types import AmoCRMTransactionElementMetadata
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderTransactionCreatorException(AmoCRMServiceException):
    """Raises when it's impossible to create customer's transaction"""


class AmoCRMOrderTransactionCreator(BaseService):
    """
    Creates customer's transaction for given order if it's paid
    Returns amocrm_id for transaction
    """

    order: Order

    quantity: int = 1  # order cannot have multiple courses

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> int:
        transaction_metadata = AmoCRMTransactionElementMetadata(
            quantity=self.quantity,
            catalog_id=self.product_catalog_id,
        )
        course_as_transaction_element = AmoCRMTransactionElement(
            id=self.order.course.amocrm_course.amocrm_id,
            metadata=transaction_metadata,
        )

        amocrm_id = self.client.create_customer_transaction(
            customer_id=self.order.user.amocrm_user.amocrm_id,
            price=self.order.price,
            order_slug=self.order.slug,
            purchased_product=course_as_transaction_element,
        )

        amocrm_order_transaction = AmoCRMOrderTransaction.objects.create(order=self.order, amocrm_id=amocrm_id)
        return amocrm_order_transaction.amocrm_id

    @property
    def product_catalog_id(self) -> int:
        return get_catalog_id(catalog_type="products")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order_is_paid,
            self.validate_transaction_doesnt_exist,
            self.validate_order_with_course,
            self.validate_amocrm_course_exist,
            self.validate_amocrm_customer_exist,
        ]

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderTransactionCreatorException("Order doesnt have a course")

    def validate_amocrm_course_exist(self) -> None:
        if not hasattr(self.order.course, "amocrm_course"):
            raise AmoCRMOrderTransactionCreatorException("Course doesn't exist in AmoCRM")

    def validate_transaction_doesnt_exist(self) -> None:
        if hasattr(self.order, "amocrm_transaction"):
            raise AmoCRMOrderTransactionCreatorException("Transaction already exist")

    def validate_order_is_paid(self) -> None:
        if self.order.paid is None:
            raise AmoCRMOrderTransactionCreatorException("Order is not paid")

    def validate_amocrm_customer_exist(self) -> None:
        if not hasattr(self.order.user, "amocrm_user"):
            raise AmoCRMOrderTransactionCreatorException("AmoCRM customer for order's user doesn't exist")
