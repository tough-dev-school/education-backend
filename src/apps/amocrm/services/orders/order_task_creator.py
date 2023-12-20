from dataclasses import dataclass
from datetime import timedelta
from typing import NamedTuple

from django.utils import timezone
from django.utils.functional import cached_property

from apps.amocrm.definitions import AmoCRMTaskType
from apps.amocrm.dto import AmoCRMLeadNoteDTO
from apps.amocrm.dto import AmoCRMLeadTaskDTO
from apps.amocrm.dto import AmoCRMOperatorDTO
from apps.orders.models import Order
from core.exceptions import AppServiceException
from core.services import BaseService


class AmoCRMOrderTaskCreatorException(AppServiceException):
    pass


class AmoCRMOrderTaskDataServiceNote(NamedTuple):
    service_name: str
    service_note: str


class AmoCRMOrderTaskData(NamedTuple):
    task_name: str
    task_type_id: AmoCRMTaskType
    task_responsible_user_email: str
    task_deadline_timedelta: timedelta = timedelta(days=3)
    service_note: AmoCRMOrderTaskDataServiceNote | None = None


@dataclass
class AmoCRMOrderTaskCreator(BaseService):
    """Create task in AmoCRM for the lead linked with the order.

    1. Locate the corresponding lead for the order.
    2. If 'service note' provided add it as 'service message' to the located lead.
    3. Look for existed not completed lead task with the same name and type. If not found — create new one.
    """

    order: Order
    task_data: AmoCRMOrderTaskData

    @cached_property
    def lead_id(self) -> int:
        if self.order.amocrm_lead:
            return self.order.amocrm_lead.amocrm_id

        return Order.objects.same_deal(self.order).filter(amocrm_lead__isnull=False).values_list("amocrm_lead__amocrm_id", flat=True)[0]

    @cached_property
    def responsible_user_id(self) -> int:
        for amo_operator in AmoCRMOperatorDTO().get():
            if amo_operator["email"] == self.task_data.task_responsible_user_email:
                return amo_operator["id"]

        raise AmoCRMOrderTaskCreatorException(f"Theres is no AmoCRM operators with email '{self.task_data.task_responsible_user_email}'")

    def act(self) -> None:
        self.validate_order()

        if self.task_data.service_note:
            AmoCRMLeadNoteDTO().create_service_message(
                lead_id=self.lead_id,
                service_name=self.task_data.service_note.service_name,
                note_text=self.task_data.service_note.service_note,
            )

        self.create_lead_task_if_needed()

    def validate_order(self) -> None:
        if self.order.amocrm_lead:
            return None
        if Order.objects.same_deal(self.order).filter(amocrm_lead__isnull=False).exists():
            return None
        raise AmoCRMOrderTaskCreatorException("There is no AmoCRM lead linked to order's deal")

    def create_lead_task_if_needed(self) -> int:
        for task in AmoCRMLeadTaskDTO().get(lead_id=self.lead_id, is_completed=False):
            if task["text"] == self.task_data.task_name and task["task_type_id"] == self.task_data.task_type_id:
                return task["id"]

        task_deadline = timezone.now() + self.task_data.task_deadline_timedelta

        return AmoCRMLeadTaskDTO().create(
            lead_id=self.lead_id,
            task_text=self.task_data.task_name,
            task_type_id=self.task_data.task_type_id,
            timestamp_complete_till=int(task_deadline.timestamp()),
            responsible_user_id=self.responsible_user_id,
        )
