from django.conf import settings
from django.utils import timezone

from app.tasks import send_happiness_message, send_mail
from orders.models import Order


class Pigwidgeon:
    """Ship the order (actualy calls item ship() method)"""
    def __init__(self, order: Order, silent: bool = False):
        self.order = order
        self.silent = silent

    def __call__(self):
        if self.ship():
            self.mark_order_as_shipped()
        self.send_notification_to_giver()
        self.send_happiness_message()

    def ship(self) -> bool:
        """Ship the order. Returns true if order is shipped"""
        if self.order.desired_shipment_date is None:
            self.order.item.ship(to=self.order.user)

            return True

        return False

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

    def send_notification_to_giver(self):
        if self.order.giver is None:
            return

        if self.order.desired_shipment_date is None:
            return

        send_mail.delay(
            to=self.order.giver.email,
            template_id='gift-notification-for-giver',  # postmark
            disable_antispam=True,
            ctx={
                'item_name': self.order.item.full_name,
                'receiver_name': str(self.order.user),
                'receiver_email': self.order.user.email,
                'desired_shipment_date': self.order.desired_shipment_date.strftime('%d.%m.%Y'),
            },
        )
