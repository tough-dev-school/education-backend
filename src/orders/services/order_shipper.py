from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from app.services import BaseService
from app.tasks import send_happiness_message
from mailing.tasks import send_mail
from orders.models import Order


@dataclass
class OrderShipper(BaseService):
    """Ship the order (actualy calls item ship() method)"""

    order: Order
    silent: bool | None = False

    def act(self) -> None:
        if self.ship():
            self.mark_order_as_shipped()

        if not self.order.notification_to_giver_is_sent:
            self.send_notification_to_giver()

        if not self.silent and self.order.price > 0:
            self.send_happiness_message()

    def ship(self) -> bool:
        """Ship the order. Returns true if order is shipped"""
        desired_date = self.order.desired_shipment_date
        if desired_date is None or desired_date <= timezone.now():
            self.order.item.ship(to=self.order.user, order=self.order)  # type: ignore

            return True

        return False

    def mark_order_as_shipped(self) -> None:
        self.order.shipped = timezone.now()
        self.order.save()

    def send_happiness_message(self) -> None:
        if not settings.HAPPINESS_MESSAGES_CHAT_ID:
            return

        sum = str(self.order.price).replace(".00", "")
        reason = str(self.order.item) if self.order.giver is None else f"{self.order.item} (подарок)"

        send_happiness_message.delay(text=f"💰+{sum} ₽, {self.order.user}, {reason}")

    def send_notification_to_giver(self) -> None:
        if self.order.giver is None:
            return

        if self.order.desired_shipment_date is None:
            return

        send_mail.delay(
            to=self.order.giver.email,
            template_id="gift-notification-for-giver",  # postmark
            disable_antispam=True,
            ctx={
                "item_name": self.order.item.full_name,
                "receiver_name": str(self.order.user),
                "receiver_email": self.order.user.email,
                "desired_shipment_date": self.order.desired_shipment_date.strftime("%d.%m.%Y"),
            },
        )

        self.order.notification_to_giver_is_sent = True
        self.order.save()
