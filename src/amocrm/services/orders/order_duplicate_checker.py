from dataclasses import dataclass
from typing import Callable

from django.db.models import QuerySet

from amocrm.exceptions import AmoCRMServiceException
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderDuplicateCheckerException(AmoCRMServiceException):
    """Raises when it's impossible to check order duplicates in amocrm"""


@dataclass
class AmoCRMOrderDuplicateChecker(BaseService):
    """
    Check for order with same course and user in amocrm

    - if there is a paid order with same course and user -> return None
    - if there is a not paid order with lead in amocrm -> link its lead to the new order and return this order
    """

    order: Order

    def act(self) -> Order | None:
        course = self.order.course
        user = self.order.user

        paid_order = Order.objects.filter(user=user, course=course, paid__isnull=False, unpaid__isnull=True).last()
        if paid_order is not None and paid_order != self.order:
            return None

        orders_with_same_user_and_course = Order.objects.filter(user=user, course=course, paid__isnull=True, unpaid__isnull=True).exclude(pk=self.order.pk)
        self.link_lead_to_new_order(orders=orders_with_same_user_and_course)

        return self.order

    def link_lead_to_new_order(self, orders: QuerySet[Order]) -> None:
        orders_with_lead = [order for order in orders if hasattr(order, "amocrm_lead")]
        if len(orders_with_lead) == 1:
            amocrm_lead = orders_with_lead[0].amocrm_lead
            amocrm_lead.order = self.order
            amocrm_lead.save()
        elif len(orders_with_lead) > 1:
            raise AmoCRMOrderDuplicateCheckerException("There are duplicates for such order with same course and user")

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order_with_course,
        ]

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderDuplicateCheckerException("Order has no course")
