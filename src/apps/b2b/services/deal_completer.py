from dataclasses import dataclass
from decimal import Decimal

from django.utils import timezone

from apps.b2b.models import Deal
from apps.orders.models import Order
from apps.orders.services import OrderCreator
from core.services import BaseService


@dataclass
class DealCompleter(BaseService):
    """Creates orders for the given deal"""

    deal: Deal

    def act(self) -> None:
        if self.deal.completed is not None:
            return

        self.create_orders(self.deal)
        self.assign_existing_orders(self.deal)
        self.mark_deal_as_complete()

    def get_single_order_price(self) -> Decimal:
        return Decimal(self.deal.price / self.deal.students.count())

    def mark_deal_as_complete(self) -> None:
        self.deal.completed = timezone.now()
        self.deal.save()

    def create_orders(self, deal: Deal) -> list[Order]:
        orders = []
        for student in deal.students.all():
            if not Order.objects.filter(user_id=student.user_id, course_id=deal.course_id).exists():
                order = OrderCreator(
                    item=deal.course,
                    price=self.get_single_order_price(),
                    user=student.user,
                    author=deal.author,
                    desired_bank="b2b",
                    deal=deal,
                )()
                orders.append(order)

        return orders

    def assign_existing_orders(self, deal: Deal) -> list[Order]:
        orders = []
        for student in deal.students.all():
            order: Order

            try:
                order = Order.objects.get(user_id=student.user_id, course_id=deal.course_id, paid__isnull=True)
            except Order.DoesNotExist:
                continue

            order.deal = deal
            order.author = deal.author
            order.save()

            orders.append(order)

        return orders
