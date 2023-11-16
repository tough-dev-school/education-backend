from dataclasses import dataclass

from apps.amocrm.dto import AmoCRMLead
from apps.amocrm.dto import AmoCRMTransaction
from apps.amocrm.exceptions import AmoCRMServiceException
from apps.amocrm.models import AmoCRMOrderLead
from apps.amocrm.models import AmoCRMOrderTransaction
from apps.orders.models import Order
from core.services import BaseService


class AmoCRMOrderPusherException(AmoCRMServiceException):
    """Raises when it's impossible to push order to amocrm"""


@dataclass
class AmoCRMOrderPusher(BaseService):
    """Push given order to amocrm"""

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
        self.create_order()

    def push_lead(self) -> None:
        existing_lead = self.get_lead()
        if existing_lead is None:
            self.create_lead()
        else:
            if existing_lead.order != self.order:
                self.relink_lead(order=self.order, lead=existing_lead)
                self.reactivate_lead_in_amocrm()

    def create_lead(self) -> None:
        lead_id = AmoCRMLead(order=self.order).create()

        self.order.update(amocrm_lead=AmoCRMOrderLead.objects.create(amocrm_id=lead_id))

    def create_order(self) -> None:
        AmoCRMLead(order=self.order).update(status="purchased")
        transaction_id = AmoCRMTransaction(order=self.order).create()

        self.order.update(amocrm_transaction=AmoCRMOrderTransaction.objects.create(amocrm_id=transaction_id))

    def get_lead(self) -> AmoCRMOrderLead | None:
        """
        Search for existing leads in AmoCRM with same user and course as in given order
        to guarantee that there will be only one AmoCRM Lead for one deal
        """
        if self.order.amocrm_lead is not None:
            return self.order.amocrm_lead

        order_with_lead = Order.objects.same_deal(order=self.order).filter(amocrm_lead__isnull=False).first()
        if order_with_lead is not None:
            return order_with_lead.amocrm_lead

    @staticmethod
    def relink_lead(order: Order, lead: AmoCRMOrderLead) -> None:
        old_order = lead.order

        old_order.update(amocrm_lead=None)
        order.update(amocrm_lead=lead)

    def reactivate_lead_in_amocrm(self) -> None:
        """Actualize lead's price, created_at and set lead to 'active' status"""
        AmoCRMLead(order=self.order).update(status="first_contact")

    def order_must_be_pushed(self) -> bool:
        if self.order.is_b2b:
            return False
        if self.order.price == 0:
            return False
        if Order.objects.paid().same_deal(order=self.order).filter(amocrm_lead__isnull=False).exists():  # we have other paid orders for the same deal
            return False

        return True
