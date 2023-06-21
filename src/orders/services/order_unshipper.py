from dataclasses import dataclass

from app.services import BaseService
from orders.models import Order


@dataclass
class OrderUnshipper(BaseService):
    order: Order

    def act(self):
        self.order.item.unship(order=self.order)

        self.mark_order_as_unpaid()
        self.mark_order_as_unshipped()

    def mark_order_as_unshipped(self):
        self.order.shipped = None
        self.order.save()

    def mark_order_as_unpaid(self):
        self.order.paid = None
        self.order.save()
