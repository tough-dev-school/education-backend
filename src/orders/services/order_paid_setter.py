from typing import Optional

from django.utils import timezone

from orders.models import Order


class OrderPaidSetter:
    """Mark order as paid"""
    def __init__(self, order: Order, silent: Optional[bool] = False):
        self.order = order
        self.silent: bool = silent
        self.is_already_paid = (order.paid is not None)
        self.is_already_shipped = (order.shipped is not None)

    def __call__(self) -> None:
        self.mark_order_as_paid()
        self.ship()

    def mark_order_as_paid(self) -> None:
        self.order.paid = timezone.now()
        if not self.is_already_paid:  # reset unpayment date if order is not paid yet
            self.order.unpaid = None

        self.order.save()

    def ship(self) -> None:
        if not self.is_already_shipped and not self.is_already_paid and self.order.item is not None:
            self.order.ship(silent=self.silent)
