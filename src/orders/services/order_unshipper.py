from dataclasses import dataclass

from app.services import BaseService
from orders.models import Order


@dataclass
class OrderUnshipper(BaseService):
    order: Order

    def act(self) -> Order:
        if self.order.shipped is not None:
            self.order.item.unship(order=self.order)
            self.mark_order_as_unshipped()

        return self.order

    def mark_order_as_unshipped(self) -> None:
        self.order.shipped = None
        self.order.save(update_fields=["shipped", "modified"])
