from dataclasses import dataclass

from django.utils import timezone

from apps.orders.models import Order
from core.services import BaseService


@dataclass
class OrderShipper(BaseService):
    """Ship the order (actually calls item ship() method)"""

    order: Order

    def act(self) -> None:
        if not self.order.shipped:
            self.ship()
            self.mark_order_as_shipped()

    def ship(self) -> None:
        """Ship the order"""
        self.order.item.ship(to=self.order.user, order=self.order)

    def mark_order_as_shipped(self) -> None:
        self.order.shipped = timezone.now()
        self.order.save(update_fields=["shipped", "modified"])
