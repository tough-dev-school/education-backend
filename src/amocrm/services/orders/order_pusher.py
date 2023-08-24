from dataclasses import dataclass

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
        if not self.order_must_be_pushed():
            return

        if self.is_paid or self.is_unpaid:
            self.push_order()
        else:
            self.push_lead()

    def push_order(self) -> None:
        from amocrm.tasks import push_existing_order_to_amocrm
        from amocrm.tasks import push_new_order_to_amocrm

        existing_lead = self.get_lead()
        if existing_lead is not None:
            push_existing_order_to_amocrm.delay(order_id=self.order.id)
        else:
            push_new_order_to_amocrm.delay(order_id=self.order.id)

    def push_lead(self) -> None:
        from amocrm.tasks import create_amocrm_lead
        from amocrm.tasks import update_amocrm_lead

        existing_lead = self.get_lead()
        if existing_lead is not None:
            update_amocrm_lead.delay(order_id=self.order.id)
        else:
            create_amocrm_lead.delay(order_id=self.order.id)

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

    def order_must_be_pushed(self) -> bool:
        if self.order.is_b2b:
            return False
        if self.order.price == 0:
            return False

        if (
            Order.objects.paid().filter(user=self.order.user, course=self.order.course).exclude(pk=self.order.pk).exists()
        ):  # we have other paid orders for the same deal
            return False

        return True
