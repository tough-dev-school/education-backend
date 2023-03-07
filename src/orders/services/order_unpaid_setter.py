from django.utils import timezone

from orders.models import Order


class OrderUnpaidSetter:
    """Mark order as not paid"""

    def __init__(self, order: Order):
        self.order = order
        self.was_paid_before_service_call = order.paid is not None

    def __call__(self):
        self.mark_order_as_not_paid()
        self.unship()

    def mark_order_as_not_paid(self):
        self.order.paid = None
        if self.was_paid_before_service_call:  # log unpayment date only if order has already been paid
            self.order.unpaid = timezone.now()

        self.order.save()

    def unship(self):
        if self.was_paid_before_service_call and self.order.item is not None:
            self.order.unship()
