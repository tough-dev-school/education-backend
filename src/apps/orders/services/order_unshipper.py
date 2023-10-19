from dataclasses import dataclass

from apps.orders.models import Order
from core.services import BaseService


@dataclass
class OrderUnshipper(BaseService):
    order: Order

    def act(self) -> None:
        self.order.item.unship(order=self.order)

        self.mark_order_as_unpaid()
        self.mark_order_as_unshipped()

    def mark_order_as_unshipped(self) -> None:
        self.order.shipped = None
        self.order.save()

    def mark_order_as_unpaid(self) -> None:
        self.order.paid = None
        self.order.save()
