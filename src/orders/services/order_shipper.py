from django.conf import settings
from django.utils import timezone

from app.tasks import send_happiness_message
from orders.models import Order


class Pigwidgeon:
    """Ship the order (actualy calls item ship() method)"""
    def __init__(self, order: Order, silent: bool = False):
        self.order = order
        self.silent = silent

    def __call__(self):
        self.ship()
        self.mark_order_as_shipped()

        order_got_shipped.send(
            sender=Order,
            order=self.order,
            silent=self.silent,
        )

    def ship(self):
        self.order.item.ship(to=self.order.user)

    def mark_order_as_shipped(self):
        self.order.shipped = timezone.now()
        self.order.save()
