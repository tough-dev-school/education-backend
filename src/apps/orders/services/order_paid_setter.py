from dataclasses import dataclass

from celery import chain

from django.utils import timezone

from apps.amocrm.tasks import amocrm_enabled
from apps.amocrm.tasks import push_order
from apps.amocrm.tasks import push_user
from apps.orders.models import Order
from apps.users.tasks import rebuild_tags
from core.services import BaseService


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
        self.ship()
        self.rebuild_user_tags()
        self.update_amocrm()

    def mark_order_as_paid(self) -> None:
        self.order.paid = timezone.now()
        if not self.is_already_paid:  # reset unpayment date if order is not paid yet
            self.order.unpaid = None

        self.order.save(update_fields=['paid', 'unpaid', 'modified'])

    def ship(self) -> None:
        if not self.is_already_shipped and not self.is_already_paid and self.order.item is not None:
            self.order.ship(silent=self.silent)

    def rebuild_user_tags(self) -> None:
        rebuild_tags.delay(student_id=self.order.user_id)

    def update_amocrm(self) -> None:
        if amocrm_enabled():
            chain(
                push_user.si(user_id=self.order.user.id),
                push_order.si(order_id=self.order.id),
            ).apply_async(
                countdown=30
            )  # hope rebuild tags are finished
