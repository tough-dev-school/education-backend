from dataclasses import dataclass

from celery import chain

from django.utils import timezone

from amocrm.tasks import amocrm_enabled
from amocrm.tasks import push_user
from amocrm.tasks import return_order
from app.services import BaseService
from orders.models import Order
from users.tasks import rebuild_tags


@dataclass
class OrderUnpaidSetter(BaseService):
    """Mark order as not paid"""

    order: Order

    def __post_init__(self) -> None:
        self.was_paid_before_service_call = self.order.paid is not None

    def act(self) -> None:
        self.mark_order_as_not_paid()
        self.unship()
        self.after_unshipment()

    def mark_order_as_not_paid(self) -> None:
        self.order.paid = None
        if self.was_paid_before_service_call:  # log unpayment date only if order has already been paid
            self.order.unpaid = timezone.now()

        self.order.save()

    def unship(self) -> None:
        if self.was_paid_before_service_call and self.order.item is not None:
            self.order.unship()

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
