from dataclasses import dataclass
from typing import Callable

from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.cache.lead_pipeline_id import get_pipeline_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderLead
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderLeadCreatorException(AmoCRMServiceException):
    """Raises when it's impossible to create customer's amocrm_lead"""


@dataclass
class AmoCRMOrderLeadCreator(BaseService):
    """
    Creates amocrm_lead for given order and with user's amocrm contact

    - if order is paid new amocrm_lead creates with 'purchased' status - else 'first_contact'

    Returns amocrm_id for amocrm_lead
    """

    order: Order

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.is_paid = self.order.paid is not None

    def act(self) -> int:
        amocrm_id = self.client.create_lead(
            status_id=self.status_id,
            pipeline_id=self.pipeline_id,
            contact_id=self.order.user.amocrm_user_contact.amocrm_id,
            price=self.order.price,
            created_at=self.order.created,
        )

        self.order.amocrm_lead = AmoCRMOrderLead.objects.create(amocrm_id=amocrm_id)
        self.order.save()
        return self.order.amocrm_lead.amocrm_id

    @property
    def pipeline_id(self) -> int:
        return get_pipeline_id(pipeline_name="b2c")

    @property
    def status_id(self) -> int:
        return self._paid_status_id if self.is_paid else self._not_paid_status_id

    @property
    def _paid_status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="purchased")

    @property
    def _not_paid_status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="first_contact")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_lead_doesnt_exist,
            self.validate_transaction_doesnt_exist,
            self.validate_order_with_course,
            self.validate_amocrm_course_exist,
            self.validate_amocrm_contact_exist,
        ]

    def validate_lead_doesnt_exist(self) -> None:
        if self.order.amocrm_lead is not None:
            raise AmoCRMOrderLeadCreatorException("Lead already exists")

    def validate_transaction_doesnt_exist(self) -> None:
        if self.order.amocrm_transaction is not None:
            raise AmoCRMOrderLeadCreatorException("Transaction for this order already exists")

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderLeadCreatorException("Order doesn't have a course")

    def validate_amocrm_course_exist(self) -> None:
        if not hasattr(self.order.course, "amocrm_course"):
            raise AmoCRMOrderLeadCreatorException("Course doesn't exist in AmoCRM")

    def validate_amocrm_contact_exist(self) -> None:
        if not hasattr(self.order.user, "amocrm_user_contact"):
            raise AmoCRMOrderLeadCreatorException("AmoCRM contact for order's user doesn't exist")
