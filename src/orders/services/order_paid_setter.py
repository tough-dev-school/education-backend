from dataclasses import dataclass

from celery import chain

from django.utils import timezone

from amocrm.tasks import amocrm_enabled
from amocrm.tasks import push_customer
from app.services import BaseService
from banking.selector import get_bank
from orders.models import Order
from users.tasks import rebuild_tags


@dataclass
class OrderPaidSetter(BaseService):
    """Mark order as paid"""

    order: Order
    silent: bool | None = False

    def __post_init__(self) -> None:
        """Save order state at boot time"""
        self.is_already_paid = self.order.paid is not None
        self.is_already_shipped = self.order.shipped is not None

    def act(self) -> None:
        self.mark_order_as_paid()
        self.call_bank_successfull_callback()
        self.ship()
        self.update_user_tags()

    def mark_order_as_paid(self) -> None:
        self.order.paid = timezone.now()
        if not self.is_already_paid:  # reset unpayment date if order is not paid yet
            self.order.unpaid = None

        self.order.save()

    def ship(self) -> None:
        if not self.is_already_shipped and not self.is_already_paid and self.order.item is not None:
            self.order.ship(silent=self.silent)

    def call_bank_successfull_callback(self) -> None:
        Bank = get_bank(self.order.bank_id)
        bank = Bank(order=self.order)
        bank.successful_payment_callback()

    def update_user_tags(self) -> None:
        can_be_subscribed = self.order.user.email and len(self.order.user.email)
        if not can_be_subscribed and not amocrm_enabled():
            rebuild_tags.delay(student_id=self.order.user.id, subscribe=False)

        if can_be_subscribed:
            if amocrm_enabled():
                tasks_chain = chain(
                    rebuild_tags.si(student_id=self.order.user.id, subscribe=True),
                    push_customer.si(user_id=self.order.user.id).set(queue="amocrm"),
                )
                tasks_chain.delay()
            else:
                rebuild_tags.delay(student_id=self.order.user.id, subscribe=True)
