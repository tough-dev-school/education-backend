from dataclasses import dataclass
from typing import Callable

from amocrm.cache.lead_b2c_pipeline_statuses_ids import get_b2c_pipeline_status_id
from amocrm.cache.lead_pipeline_id import get_pipeline_id
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
        self.is_paid = self.order.paid is not None
        self.is_unpaid = self.order.unpaid is not None

    def act(self) -> int:
        return self.client.update_lead(
            lead_id=self.amocrm_lead.amocrm_id,
            status_id=self.status_id,
            pipeline_id=self.pipeline_id,
            price=self.order.price,
            created_at=self.order.created,
        )

    @property
    def pipeline_id(self) -> int:
        return get_pipeline_id(pipeline_name="b2c")

    @property
    def status_id(self) -> int:
        if self.is_unpaid:
            return self._unpaid_status_id
        elif self.is_paid:
            return self._paid_status_id
        return self._not_paid_or_unpaid_status_id if self.order.price != 0 else self._unpaid_status_id

    @property
    def _paid_status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="purchased")

    @property
    def _unpaid_status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="closed")

    @property
    def _not_paid_or_unpaid_status_id(self) -> int:
        return get_b2c_pipeline_status_id(status_name="first_contact")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_transaction_doesnt_exist_if_paid,
            self.validate_order_with_course,
            self.validate_amocrm_course_exist,
            self.validate_amocrm_contact_exist,
        ]

    def validate_transaction_doesnt_exist_if_paid(self) -> None:
        if hasattr(self.order, "amocrm_transaction") and self.is_paid and self.order.price != 0:
            raise AmoCRMOrderLeadUpdaterException("Transaction for this paid order already exists")

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderLeadUpdaterException("Order doesn't have a course")

    def validate_amocrm_course_exist(self) -> None:
        if not hasattr(self.order.course, "amocrm_course"):
            raise AmoCRMOrderLeadUpdaterException("Course doesn't exist in AmoCRM")

    def validate_amocrm_contact_exist(self) -> None:
        if not hasattr(self.order.user, "amocrm_user_contact"):
            raise AmoCRMOrderLeadUpdaterException("AmoCRM contact for order's user doesn't exist")
