from dataclasses import dataclass
from typing import Callable

from celery import chain

from django.utils import timezone

from amocrm.tasks import amocrm_enabled
from amocrm.tasks import push_user
from amocrm.tasks import return_order
from app.services import BaseService
from banking.selector import REFUNDABLE_BANK_KEYS
from orders.models import Order
from orders.services import OrderBankRefunder
from users.tasks import rebuild_tags


class OrderRefunderException(Exception):
    pass


@dataclass
class OrderRefunder(BaseService):
    """Refund and unship order. If order is suitable for bank refund - do it."""

    order: Order

    def act(self) -> None:
        if self.order.bank_id in REFUNDABLE_BANK_KEYS:
            OrderBankRefunder(order=self.order)()
        else:
            self.mark_order_as_not_paid()

        self.order.unship()
        self.after_unshipment()

    def mark_order_as_not_paid(self) -> None:
        self.order.unpaid = timezone.now()
        self.order.save(update_fields=["unpaid", "modified"])

    def after_unshipment(self) -> None:
        can_be_subscribed = bool(self.order.user.email and len(self.order.user.email))

        if not can_be_subscribed and not amocrm_enabled():
            rebuild_tags.delay(student_id=self.order.user.id, subscribe=False)
            return None

        if amocrm_enabled():
            chain(
                rebuild_tags.si(student_id=self.order.user.id, subscribe=can_be_subscribed),
                push_user.si(user_id=self.order.user.id),
                return_order.si(order_id=self.order.id),
            ).delay()

    def get_validators(self) -> list[Callable]:
        return [self.validate_order]

    def validate_order(self) -> None:
        if not self.order.paid:
            raise OrderRefunderException("Order is not paid")
