from dataclasses import dataclass
from typing import Callable

from amocrm.exceptions import AmoCRMServiceException
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderPusherException(AmoCRMServiceException):
    """Raises when it's impossible to push order to amocrm"""


@dataclass
class AmoCRMOrderPusher(BaseService):
    """
    Push given order to amocrm

    if order already is in amocrm - update it
    else - create lead and transaction if needed
    """

    order: Order

    def act(self) -> None:
        if not self.order_must_be_pushed(order=self.order):
            return None

        duplicate_order = self.look_for_duplicate_order(order=self.order)
        if duplicate_order is not None:
            self.link_lead_to_new_order(duplicate_order_with_lead=duplicate_order)

        if hasattr(self.order, "amocrm_lead"):
            self.push_existing_order_to_amocrm(order=self.order)
        else:
            self.push_new_order_to_amocrm(order=self.order)

    def link_lead_to_new_order(self, duplicate_order_with_lead: Order) -> None:
        amocrm_lead = duplicate_order_with_lead.amocrm_lead
        amocrm_lead.order = self.order
        amocrm_lead.save()

    @staticmethod
    def order_must_be_pushed(order: Order) -> bool:
        if order.is_b2b:
            return False
        if order.price == 0:
            return False

        paid_order = Order.objects.filter(user=order.user, course=order.course, paid__isnull=False, unpaid__isnull=True).last()
        if paid_order is not None and paid_order != order:
            return False

        return True

    @staticmethod
    def look_for_duplicate_order(order: Order) -> Order | None:
        """Returns duplicate order if exists else None"""
        course = order.course
        user = order.user

        orders_with_same_user_and_course = Order.objects.filter(user=user, course=course, paid__isnull=True, unpaid__isnull=True).exclude(pk=order.pk)
        orders_with_lead = [order for order in orders_with_same_user_and_course if hasattr(order, "amocrm_lead")]
        if len(orders_with_lead) > 1:
            raise AmoCRMOrderPusherException("There are duplicates for such order with same course and user")

        return orders_with_lead[0] if len(orders_with_lead) == 1 else None

    @staticmethod
    def push_existing_order_to_amocrm(order: Order) -> None:
        from amocrm.tasks import push_existing_order_to_amocrm

        push_existing_order_to_amocrm.delay(order_id=order.id)

    @staticmethod
    def push_new_order_to_amocrm(order: Order) -> None:
        from amocrm.tasks import push_new_order_to_amocrm

        push_new_order_to_amocrm.delay(order_id=order.id)

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order_with_course,
        ]

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderPusherException("Order has no course")
