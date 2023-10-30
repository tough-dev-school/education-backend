from dataclasses import dataclass

from apps.orders.models import Order
from core.services import BaseService


@dataclass
class OrderUnshipper(BaseService):
    order: Order

    def act(self) -> Order:
        if self.order.shipped is not None:
            self.unship_item()
            self.mark_order_as_unshipped()

        return self.order

    def unship_item(self) -> None:
        if self.order.item is not None:
            self.order.item.unship(order=self.order)

    def mark_order_as_unshipped(self) -> None:
        self.order.shipped = None
        self.order.save(update_fields=["shipped", "modified"])
