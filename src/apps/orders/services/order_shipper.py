from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

from apps.orders import human_readable
from apps.orders.models import Order
from core.services import BaseService
from core.tasks import send_telegram_message


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

        send_telegram_message.delay(
            chat_id=settings.HAPPINESS_MESSAGES_CHAT_ID,
            text=self.get_order_happiness_message(self.order),
        )

    @staticmethod
    def get_order_happiness_message(order: Order) -> str:
        sum = str(order.price).replace(".00", "")
        reason = str(order.item)
        payment_method = human_readable.get_order_payment_method_name(order)

        payment_info = f"💰+{sum} ₽, {payment_method}"

        if order.promocode:
            payment_info += f", промокод {order.promocode}"

        return f"{payment_info}\n{reason}\n{order.user}"
