from dataclasses import dataclass

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.lead_b2c_pipeline_id import get_b2c_pipeline_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMOrderTransaction
from amocrm.types import AmoCRMTransactionElement
from amocrm.types import AmoCRMTransactionElementMetadata
from app.services import BaseService
from orders.models import Order


@dataclass
class AmoCRMOrderCreator(BaseService):
    """
    Updates amocrm_lead for given paid order and creates transaction

    Returns amocrm_id for amocrm_lead
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> int:
        lead_amocrm_id = self.update_lead_status()
        self.create_transaction()

        return lead_amocrm_id

    def update_lead_status(self) -> int:
        return self.client.update_lead(
            lead_id=self.order.amocrm_lead.amocrm_id,  # type: ignore
            status_id=get_b2c_pipeline_status_id(status_name="purchased"),
            pipeline_id=get_b2c_pipeline_id(),
            price=self.order.price,
            created_at=self.order.created,
        )

    def create_transaction(self) -> None:
        transaction_metadata = AmoCRMTransactionElementMetadata(
            catalog_id=get_catalog_id(catalog_type="products"),
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

        self.order.amocrm_transaction = AmoCRMOrderTransaction.objects.create(amocrm_id=amocrm_id)
        self.order.save()
