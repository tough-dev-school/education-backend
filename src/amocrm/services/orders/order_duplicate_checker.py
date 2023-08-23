from dataclasses import dataclass
from typing import Callable

from amocrm.exceptions import AmoCRMServiceException
from app.services import BaseService
from orders.models import Order


class AmoCRMOrderDuplicateCheckerException(AmoCRMServiceException):
    """Raises when it's impossible to check order duplicates in amocrm"""


@dataclass
class AmoCRMOrderDuplicateChecker(BaseService):
    """
    Check for order with same course and user in amocrm

    - if there is a not paid order with lead in amocrm -> return such an order
    - if there is not -> return None
    """

    order: Order

    def act(self) -> Order | None:
        course = self.order.course
        user = self.order.user

        orders_with_same_user_and_course = Order.objects.filter(user=user, course=course, paid__isnull=True, unpaid__isnull=True).exclude(pk=self.order.pk)
        orders_with_lead = [order for order in orders_with_same_user_and_course if hasattr(order, "amocrm_lead")]
        if len(orders_with_lead) > 1:
            raise AmoCRMOrderDuplicateCheckerException("There are duplicates for such order with same course and user")

        return orders_with_lead[0] if len(orders_with_lead) == 1 else None

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_order_with_course,
        ]

    def validate_order_with_course(self) -> None:
        if self.order.course is None:
            raise AmoCRMOrderDuplicateCheckerException("Order has no course")
