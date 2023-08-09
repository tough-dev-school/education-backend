from dataclasses import dataclass
from typing import Callable

from django.utils.functional import cached_property

from amocrm.cache.lead_b2b_pipeline_statuses_ids import get_b2b_pipeline_status_id
from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderLead
from app.services import BaseService


class AmoCRMOrderLeadUpdaterException(AmoCRMServiceException):
    """Raises when it's impossible to update amocrm_lead"""


@dataclass
class AmoCRMOrderLeadUpdater(BaseService):
    """
    Updates amocrm_lead for given order
    Move to purchased status and updates price

    Returns amocrm_id for amocrm_lead
    """

    amocrm_lead: AmoCRMOrderLead

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.order = self.amocrm_lead.order

    def act(self) -> int:
        return self.client.update_lead(
            lead_id=self.amocrm_lead.amocrm_id,
            status_id=self.status_id,
            price=self.order.price,
        )

    @cached_property
    def is_b2b(self) -> bool:
        return "b2b" in self.order.user.tags

    @property
    def status_id(self) -> int:
        return get_b2b_pipeline_status_id(status_name="purchased") if self.is_b2b else get_b2c_pipeline_status_id(status_name="purchased")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order_is_paid,
            self.validate_transaction_doesnt_exist,
            self.validate_order_with_course,
            self.validate_amocrm_course_exist,
            self.validate_amocrm_contact_exist,
        ]

    def validate_order_is_paid(self) -> None:
        if self.order.paid is None:
            raise AmoCRMOrderLeadUpdaterException("Order must be paid")

    def validate_transaction_doesnt_exist(self) -> None:
        if hasattr(self.order, "amocrm_transaction"):
            raise AmoCRMOrderLeadUpdaterException("Transaction for this order already exists")

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderLeadUpdaterException("Order doesn't have a course")

    def validate_amocrm_course_exist(self) -> None:
        if not hasattr(self.order.course, "amocrm_course"):
            raise AmoCRMOrderLeadUpdaterException("Course doesn't exist in AmoCRM")

    def validate_amocrm_contact_exist(self) -> None:
        if not hasattr(self.order.user, "amocrm_user_contact"):
            raise AmoCRMOrderLeadUpdaterException("AmoCRM contact for order's user doesn't exist")
