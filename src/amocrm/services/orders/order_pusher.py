from dataclasses import dataclass

from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMOrderLead
from amocrm.services.orders.lead_creator import AmoCRMLeadCreator
from amocrm.services.orders.lead_updater import AmoCRMLeadUpdater
from amocrm.services.orders.order_creator import AmoCRMOrderCreator
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

        if self.order.paid is not None:
            self.push_order()
        else:
            self.push_lead()

    def push_order(self) -> None:
        existing_lead = self.get_lead()
        if existing_lead is None:
            raise AmoCRMOrderPusherException("Cannot push paid order without existing lead")
        if existing_lead.order != self.order:
            self.relink_lead(order=self.order, lead=existing_lead)
        AmoCRMOrderCreator(order=self.order)()

    def push_lead(self) -> None:
        existing_lead = self.get_lead()
        if existing_lead is None:
            AmoCRMLeadCreator(order=self.order)()
        else:
            if existing_lead.order != self.order:
                self.relink_lead(order=self.order, lead=existing_lead)
                AmoCRMLeadUpdater(order=self.order)()

    def get_lead(self) -> AmoCRMOrderLead | None:
        if self.order.amocrm_lead is not None:
            return self.order.amocrm_lead

        order_with_lead = Order.objects.same_deal(order=self.order).filter(amocrm_lead__isnull=False).first()
        if order_with_lead is not None:
            return order_with_lead.amocrm_lead

    def relink_lead(self, order: Order, lead: AmoCRMOrderLead) -> None:
        old_order = lead.order
        old_order.amocrm_lead = None
        old_order.save()
        order.amocrm_lead = lead
        order.save()

    def order_must_be_pushed(self) -> bool:
        if self.order.is_b2b:
            return False
        if self.order.price == 0:
            return False
        if Order.objects.paid().same_deal(order=self.order).filter(amocrm_lead__isnull=False).exists():  # we have other paid orders for the same deal
            return False

        return True
