from dataclasses import dataclass
from typing import Callable

from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderLead
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderPusherException(AmoCRMServiceException):
    """Raises when it's impossible to push order to amocrm"""


@dataclass
class AmoCRMOrderPusher(BaseService):
    """
    Push given order to amocrm
    """

    order: Order

    def __post_init__(self) -> None:
        self.is_paid = self.order.paid is not None
        self.is_unpaid = self.order.unpaid is not None

    def act(self) -> None:
        if not self.order_must_be_pushed(order=self.order):
            return

        if self.is_paid or self.is_unpaid:
            self.push_order()
        else:
            self.push_lead()

    def push_order(self) -> None:
        existing_lead = self.get_lead()
        if existing_lead is not None:
            self.update_order_in_amocrm()
        else:
            self.create_order_in_amocrm()

    def push_lead(self) -> None:
        existing_lead = self.get_lead()
        if existing_lead is not None:
            self.update_lead()
        else:
            self.create_lead()

    def get_lead(self) -> AmoCRMOrderLead | None:
        if hasattr(self.order, "amocrm_lead"):
            return self.order.amocrm_lead

        orders_with_same_user_and_course = Order.objects.filter(user=self.order.user, course=self.order.course).exclude(pk=self.order.pk)
        orders_with_lead = [order for order in orders_with_same_user_and_course if hasattr(order, "amocrm_lead")]

        if len(orders_with_lead) == 1:
            existing_lead = orders_with_lead[0].amocrm_lead
            self.link_lead_to_new_order(existing_lead=existing_lead)
            return existing_lead

        if len(orders_with_lead) > 1:
            raise AmoCRMOrderPusherException("There are duplicates leads for such order with same course and user")

    def link_lead_to_new_order(self, existing_lead: AmoCRMOrderLead) -> None:
        existing_lead.order = self.order
        existing_lead.save()

    def update_lead(self) -> None:
        from amocrm.tasks import update_amocrm_lead

        update_amocrm_lead.delay(order_id=self.order.id)

    def create_lead(self) -> None:
        from amocrm.tasks import create_amocrm_lead

        create_amocrm_lead.delay(order_id=self.order.id)

    def update_order_in_amocrm(self) -> None:
        from amocrm.tasks import push_existing_order_to_amocrm

        push_existing_order_to_amocrm.delay(order_id=self.order.id)

    def create_order_in_amocrm(self) -> None:
        from amocrm.tasks import push_new_order_to_amocrm

        push_new_order_to_amocrm.delay(order_id=self.order.id)

    @staticmethod
    def order_must_be_pushed(order: Order) -> bool:
        if order.is_b2b:
            return False
        if order.price == 0:
            return False

        if Order.objects.paid().filter(user=order.user, course=order.course).excude(pk=self.order.pk).exists()  # we have other paid orders for the same deal
           return False
        if paid_order is not None and paid_order != order:
            return False

        return True

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order_with_course,
        ]

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderPusherException("Order has no course")
