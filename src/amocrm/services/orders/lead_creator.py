from dataclasses import dataclass
from typing import Callable

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.lead_b2c_pipeline_id import get_b2c_pipeline_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderLead
from amocrm.types import AmoCRMEntityLink
from amocrm.types import AmoCRMEntityLinkMetadata
from app.services import BaseService
from orders.models import Order


class AmoCRMLeadCreatorException(AmoCRMServiceException):
    """Raises when it's impossible to create customer's amocrm_lead"""


@dataclass
class AmoCRMLeadCreator(BaseService):
    """
    Creates amocrm_lead for given order and with user's amocrm contact

    - if order is paid new amocrm_lead creates with 'purchased' status - else 'first_contact'

    Returns amocrm_id for amocrm_lead
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> None:
        lead_id = self.create_lead_id()
        self.link_course_to_lead(lead_id=lead_id)
        self.update_lead_price(lead_id=lead_id)  # update lead price, cuz the particular order price might be different from the course price
        self.save_lead_id(lead_id=lead_id)

    def create_lead_id(self) -> int:
        return self.client.create_lead(
            status_id=get_b2c_pipeline_status_id(status_name="first_contact"),
            pipeline_id=get_b2c_pipeline_id(),
            contact_id=self.order.user.amocrm_user_contact.amocrm_id,
            price=self.order.price,
            created_at=self.order.created,
        )

    def save_lead_id(self, lead_id: int) -> None:
        self.order.amocrm_lead = AmoCRMOrderLead.objects.create(amocrm_id=lead_id)
        self.order.save()

    def link_course_to_lead(self, lead_id: int) -> None:
        amocrm_course_to_link = AmoCRMEntityLink(
            to_entity_id=self.order.course.amocrm_course.amocrm_id,
            to_entity_type="catalog_elements",
            metadata=AmoCRMEntityLinkMetadata(
                catalog_id=get_catalog_id(catalog_type="products"),
            ),
        )

        self.client.link_entity_to_another_entity(
            entity_type="leads",
            entity_id=lead_id,
            entity_to_link=amocrm_course_to_link,
        )

    def update_lead_price(self, lead_id: int) -> int:
        """
        После связывания Сделки и Товара, у сделки автоматически выставляется бюджет равный цене товара
        У нас цена Заказа и Курса вполне может различаться при использовании промокода
        Поэтому после связывания нужно отправить еще запрос и установить актуальную цену Заказа
        """
        return self.client.update_lead(
            lead_id=lead_id,
            status_id=get_b2c_pipeline_status_id(status_name="first_contact"),
            pipeline_id=get_b2c_pipeline_id(),
            price=self.order.price,
            created_at=self.order.created,
        )

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_lead_doesnt_exist,
            self.validate_transaction_doesnt_exist,
            self.validate_amocrm_course_exist,
            self.validate_amocrm_contact_exist,
        ]

    def validate_lead_doesnt_exist(self) -> None:
        if self.order.amocrm_lead is not None:
            raise AmoCRMLeadCreatorException("Lead already exists")

    def validate_transaction_doesnt_exist(self) -> None:
        if self.order.amocrm_transaction is not None:
            raise AmoCRMLeadCreatorException("Transaction for this order already exists")

    def validate_amocrm_course_exist(self) -> None:
        if not hasattr(self.order.course, "amocrm_course"):
            raise AmoCRMLeadCreatorException("Course doesn't exist in AmoCRM")

    def validate_amocrm_contact_exist(self) -> None:
        if not hasattr(self.order.user, "amocrm_user_contact"):
            raise AmoCRMLeadCreatorException("AmoCRM contact for order's user doesn't exist")
