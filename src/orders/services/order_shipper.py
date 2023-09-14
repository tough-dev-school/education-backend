from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from app.services import BaseService
from app.tasks import send_happiness_message
from orders.models import Order


@dataclass
class OrderShipper(BaseService):
    """Ship the order (actually calls item ship() method)"""

    order: Order
    silent: bool | None = False

    def act(self) -> None:
        if not self.order.shipped:
            self.ship()
            self.mark_order_as_shipped()

        if not self.silent and self.order.price > 0:
            self.send_happiness_message()

    def ship(self) -> None:
        """Ship the order"""
        self.order.item.ship(to=self.order.user, order=self.order)

    def mark_order_as_shipped(self) -> None:
        self.order.shipped = timezone.now()
        self.order.save()

    def send_happiness_message(self) -> None:
        if not settings.HAPPINESS_MESSAGES_CHAT_ID:
            return

        send_happiness_message.delay(text=self.get_order_happiness_message(self.order))

    @staticmethod
    def get_order_happiness_message(order: Order) -> str:
        sum = str(order.price).replace(".00", "")
        reason = str(order.item)
        payment_method = order.get_payment_method()

        payment_info = f"💰+{sum} ₽, {payment_method}"

        if order.promocode:
            payment_info += f", промокод {order.promocode}"

        return f"{payment_info}\n{reason}\n{order.user}"
