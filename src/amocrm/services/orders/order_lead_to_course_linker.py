from dataclasses import dataclass
from typing import Callable

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderLead
from amocrm.types import AmoCRMEntityLink
from amocrm.types import AmoCRMEntityLinkMetadata
from app.services import BaseService


class AmoCRMOrderLeadToCourseLinkerException(AmoCRMServiceException):
    """Raises when it's impossible to create link between an amocrm_lead and amocrm_course"""


@dataclass
class AmoCRMOrderLeadToCourseLinker(BaseService):
    """
    Creates link between an amocrm_lead and amocrm_course as a product catalog element
    """

    amocrm_lead: AmoCRMOrderLead

    quantity: int = 1  # order can contain only 1 course

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.order = self.amocrm_lead.order

    def act(self) -> None:
        amocrm_course_to_link = AmoCRMEntityLink(
            to_entity_id=self.order.course.amocrm_course.amocrm_id,
            to_entity_type="catalog_elements",
            metadata=self.get_metadata_for_entity_to_link(),
        )

        self.client.link_entity_to_another_entity(
            entity_type="leads",
            entity_id=self.amocrm_lead.amocrm_id,
            entity_to_link=amocrm_course_to_link,
        )

    def get_metadata_for_entity_to_link(self) -> AmoCRMEntityLinkMetadata:
        return AmoCRMEntityLinkMetadata(
            quantity=self.quantity,
            catalog_id=self.products_catalog_id,
        )

    @property
    def products_catalog_id(self) -> int:
        return get_catalog_id(catalog_type="products")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_transaction_doesnt_exist,
            self.validate_amocrm_course_exist,
        ]

    def validate_transaction_doesnt_exist(self) -> None:
        if hasattr(self.order, "amocrm_transaction"):
            raise AmoCRMOrderLeadToCourseLinkerException("Transaction for this lead already exists")

    def validate_amocrm_course_exist(self) -> None:
        if not hasattr(self.order.course, "amocrm_course"):
            raise AmoCRMOrderLeadToCourseLinkerException("AmoCRMCourse for this lead doesn't exist")
