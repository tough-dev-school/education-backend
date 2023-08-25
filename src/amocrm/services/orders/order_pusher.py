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

    def act(self) -> None:
        if not self.order_must_be_pushed():
            return

        if self.order.paid is not None or self.order.unpaid is not None:
            self.push_order()
        else:
            self.push_lead()

    def push_order(self) -> None:
        from amocrm.tasks import push_existing_order_to_amocrm

        existing_lead = self.get_lead()
        if existing_lead is None:
            raise AmoCRMOrderPusherException("Cannot push paid or unpaid order without existing lead")
        if existing_lead.order != self.order:
            self.link_existing_lead_to_current_order(existing_lead=existing_lead)

        push_existing_order_to_amocrm.apply_async(kwargs=dict(order_id=self.order.id), countdown=1)

    def push_lead(self) -> None:
        from amocrm.tasks import create_amocrm_lead
        from amocrm.tasks import update_amocrm_lead

        existing_lead = self.get_lead()
        if existing_lead is None:
            create_amocrm_lead.apply_async(kwargs=dict(order_id=self.order.id), countdown=1)
        else:
            if existing_lead.order != self.order:
                self.link_existing_lead_to_current_order(existing_lead=existing_lead)
            update_amocrm_lead.apply_async(kwargs=dict(order_id=self.order.id), countdown=1)

    def get_lead(self) -> AmoCRMOrderLead | None:
        if self.order.amocrm_lead is not None:
            return self.order.amocrm_lead

        order_with_lead = Order.objects.same_deal(order=self.order).filter(amocrm_lead__isnull=False).first()
        if order_with_lead is not None:
            return order_with_lead.amocrm_lead

    def link_existing_lead_to_current_order(self, existing_lead: AmoCRMOrderLead) -> None:
        old_order = existing_lead.order
        old_order.amocrm_lead = None
        old_order.save()
        self.order.amocrm_lead = existing_lead
        self.order.save()

    def order_must_be_pushed(self) -> bool:
        if self.order.is_b2b:
            return False
        if self.order.price == 0:
            return False
        if Order.objects.paid().same_deal(order=self.order).filter(amocrm_lead__isnull=False).exists():  # we have other paid orders for the same deal
            return False

        return True
