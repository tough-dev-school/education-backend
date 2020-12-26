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
        self.send_happiness_message()

    def ship(self):
        if self.order.desired_shipment_date is None:
            self.order.item.ship(to=self.order.user)

    def mark_order_as_shipped(self):
        self.order.shipped = timezone.now()
        self.order.save()

    def send_happiness_message(self):
        if not settings.SEND_HAPPINESS_MESSAGES:
            return

        if self.silent:
            return

        send_happiness_message.delay(text='💰+{sum} ₽, {user}, {reason}'.format(
            sum=str(self.order.price).replace('.00', ''),
            user=str(self.order.user),
            reason=str(self.order.item),
        ))
