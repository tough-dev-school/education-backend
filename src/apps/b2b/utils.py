from decimal import Decimal

from django.db.models import F

from apps.b2b.models import Deal
from apps.orders.models import Order
from apps.orders.services import OrderCreator


def create_orders(deal: Deal, single_order_price: Decimal) -> list[Order]:
    orders = []
    for student in deal.students.all():
        if not Order.objects.filter(user_id=student.user_id, course_id=deal.course_id).exclude(author=F("user")).exists():
            order = OrderCreator(
                item=deal.course,
                price=single_order_price,
                user=student.user,
                author=deal.author,
                desired_bank="b2b",
                deal=deal,
            )()
            orders.append(order)

    return orders


def assign_existing_orders(deal: Deal) -> list[Order]:
    orders = []
    for student in deal.students.all():
        order = Order.objects.filter(user_id=student.user_id, course_id=deal.course_id, paid__isnull=True).exclude(author=F("user")).first()
        if order is None:
            continue

        order.deal = deal
        order.author = deal.author
        order.save()

        orders.append(order)

    return orders


__all__ = [
    "assign_existing_orders",
    "create_orders",
]
