from dataclasses import dataclass

from django.utils import timezone

from apps.orders.models import Order
from core.services import BaseService
from django.contrib.admin.models import CHANGE
from django.contrib.contenttypes.models import ContentType
from core.tasks import write_admin_log
from core.current_user import get_current_user

@dataclass
class OrderShipper(BaseService):
    """Ship the order (actually calls item ship() method)"""

    order: Order
    silent: bool | None = False

    def act(self) -> None:
        if not self.order.shipped:
            self.ship()
            self.mark_order_as_shipped()
            self.write_success_admin_log()

    @property
    def log(self) -> str:
        return "Order shipped without payment" if self.silent else "Order shipped"

    def ship(self) -> None:
        """Ship the order"""
        self.order.item.ship(to=self.order.user, order=self.order)

    def mark_order_as_shipped(self) -> None:
        self.order.shipped = timezone.now()
        self.order.save(update_fields=["shipped", "modified"])

    def write_success_admin_log(self) -> None:
        write_admin_log.delay(
            action_flag=CHANGE,
            change_message=self.log,
            content_type_id=ContentType.objects.get_for_model(self.order).id,
            object_id=self.order.id,
            object_repr=str(self.order),
            user_id=get_current_user().id,
        )
