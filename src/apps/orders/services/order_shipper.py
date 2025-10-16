from dataclasses import dataclass

from django.contrib.admin.models import CHANGE
from django.utils import timezone

from apps.orders.models import Order
from core.current_user import get_current_user
from core.services import BaseService
from core.tasks.write_admin_log import write_admin_log


@dataclass
class OrderShipper(BaseService):
    """Ship the order (actually calls item ship() method)"""

    order: Order

    def act(self) -> None:
        if not self.order.shipped:
            self.ship()
            self.mark_order_as_shipped()
            self.write_auditlog()

    def ship(self) -> None:
        """Ship the order"""
        self.order.item.ship(to=self.order.user, order=self.order)

    def mark_order_as_shipped(self) -> None:
        self.order.shipped = timezone.now()
        self.order.save(update_fields=["shipped", "modified"])

    def write_auditlog(self) -> None:
        user = get_current_user() or self.order.user  # order may be shipped anonymously, we assume customer made it

        write_admin_log.delay(
            action_flag=CHANGE,
            change_message="Order shipped",
            model="orders.Order",
            object_id=self.order.id,
            user_id=user.id,
        )
