from dataclasses import dataclass
from decimal import Decimal

from django.conf import settings
from django.contrib.admin.models import CHANGE
from django.utils import timezone

from apps.b2b.models import Deal
from apps.b2b.utils import assign_existing_orders, create_orders
from apps.orders.models import Order
from core.current_user import get_current_user
from core.pricing import format_price
from core.services import BaseService
from core.tasks import send_telegram_message, write_admin_log


@dataclass
class DealCompleter(BaseService):
    """Creates orders for the given deal"""

    deal: Deal
    ship_only: bool | None = False

    def act(self) -> None:
        if self.deal.completed is not None:
            return

        orders: list[Order] = []

        orders += create_orders(deal=self.deal, single_order_price=self.get_single_order_price())
        orders += assign_existing_orders(deal=self.deal)

        if not self.ship_only:
            self.pay_and_ship(orders)  # this will pay and ship them
            self.send_happiness_message()
            self.mark_deal_as_complete()
            self.write_auditlog()
        else:
            self.ship_without_payment(orders)  # this will only ship
            self.mark_deal_as_shipped_without_payment()
            self.write_auditlog()

    def get_single_order_price(self) -> Decimal:
        try:
            return Decimal(self.deal.price / self.deal.students.count())
        except ArithmeticError:
            return Decimal(0)

    def mark_deal_as_complete(self) -> None:
        self.deal.completed = timezone.now()
        self.deal.save()

    def mark_deal_as_shipped_without_payment(self) -> None:
        self.deal.shipped_without_payment = timezone.now()
        self.deal.save()

    @staticmethod
    def pay_and_ship(orders: list[Order]) -> None:
        for order in orders:
            order.set_paid(silent=True)

    @staticmethod
    def ship_without_payment(orders: list[Order]) -> None:
        for order in orders:
            order.ship_without_payment()

    def send_happiness_message(self) -> None:
        if not settings.HAPPINESS_MESSAGES_CHAT_ID:
            return

        send_telegram_message.delay(
            chat_id=settings.HAPPINESS_MESSAGES_CHAT_ID,
            text=f"💰+{format_price(self.deal.price)} ₽, {self.deal.customer}, продавец {self.deal.author}",
        )

    def write_auditlog(self) -> None:
        user = get_current_user()
        if user is None:
            raise RuntimeError("Cannot determine user")

        write_admin_log.delay(
            action_flag=CHANGE,
            app="b2b",
            change_message="Deal shipped without payment" if self.ship_only else "Deal completed",
            model="Deal",
            object_id=self.deal.id,
            user_id=user.id,
        )
