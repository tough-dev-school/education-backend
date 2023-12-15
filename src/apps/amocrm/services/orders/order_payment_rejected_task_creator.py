from dataclasses import dataclass
from datetime import timedelta
from typing import ClassVar

from django.utils import timezone
from django.utils.functional import cached_property

from apps.amocrm.dto import AmoCRMNoteDTO
from apps.amocrm.dto import AmoCRMOperatorDTO
from apps.amocrm.dto import AmoCRMTaskDTO
from apps.amocrm.dto.tasks import AmoCRMTaskType
from apps.orders.models import Order
from core.exceptions import AppServiceException
from core.services import BaseService


class AmoCRMPaymentRejectedTaskCreatorException(AppServiceException):
    pass


@dataclass
class AmoCRMPaymentRejectedTaskCreator(BaseService):
    """Locate the corresponding lead for the order and create a task to contact with the customer.

    Additionally, add a note on the associated AmoCRM lead specifying the reason for the rejection.
    """

    order: Order
    reject_reason: str

    task_name: ClassVar[str] = "Отказ платёжной системы"
    task_type_id: ClassVar[AmoCRMTaskType] = AmoCRMTaskType.CONTACT
    task_responsible_user_email: ClassVar[str] = "zoya@tough.school"
    lead_note_service_name: ClassVar[str] = "🤖 🏦 🤖"

    @cached_property
    def lead_id(self) -> int:
        if self.order.amocrm_lead:
            return self.order.amocrm_lead.amocrm_id

        return Order.objects.same_deal(self.order).filter(amocrm_lead__isnull=False).values_list("amocrm_lead__amocrm_id", flat=True)[0]

    @cached_property
    def responsible_user_id(self) -> int:
        for amo_operator in AmoCRMOperatorDTO().get_users():
            if amo_operator["email"] == self.task_responsible_user_email:
                return amo_operator["id"]

        raise AmoCRMPaymentRejectedTaskCreatorException(f"Theres is no AmoCRM operators with email '{self.task_responsible_user_email}'")

    def act(self) -> None:
        self.validate_order()

        AmoCRMNoteDTO().create_lead_note(
            lead_id=self.lead_id,
            service_name=self.lead_note_service_name,
            note_text=self.reject_reason,
        )

        self.create_lead_task_if_needed()

    def validate_order(self) -> None:
        if self.order.amocrm_lead:
            return None
        if Order.objects.same_deal(self.order).filter(amocrm_lead__isnull=False).exists():
            return None
        raise AmoCRMPaymentRejectedTaskCreatorException("There is no amocrm lead bound to order's deal")

    def create_lead_task_if_needed(self) -> int:
        for task in AmoCRMTaskDTO().get_lead_tasks(self.lead_id, is_completed=False):
            if task["text"] == self.task_name and task["task_type_id"] == self.task_type_id:
                return task["id"]

        tomorrow = timezone.now() + timedelta(days=3)

        return AmoCRMTaskDTO().create_lead_task(
            lead_id=self.lead_id,
            task_text=self.task_name,
            task_type_id=self.task_type_id,
            timestamp_complete_till=int(tomorrow.timestamp()),
            responsible_user_id=self.responsible_user_id,
        )
