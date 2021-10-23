from django.utils import timezone

from orders.models import Order


class OrderIsPaidSetter:
    """Mark order as paid"""
    def __init__(self, order: Order, silent=False):
        self.order = order
        self.silent = silent
        self.is_already_paid = (order.paid is not None)

    def __call__(self):
        self.mark_order_as_paid()
        self.ship()

    def mark_order_as_paid(self):
        self.order.paid = timezone.now()
        if not self.is_already_paid:  # reset unpayment date if order is not paid yet
            self.order.unpaid = None
        self.order.save()

    def ship(self):
        if not self.is_already_paid and self.order.item is not None:
            self.order.ship(silent=self.silent)
