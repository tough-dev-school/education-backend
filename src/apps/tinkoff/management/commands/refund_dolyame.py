from django.core.management.base import BaseCommand

from apps.orders.models import Order
from apps.tinkoff.dolyame import Dolyame


class Command(BaseCommand):
    def add_arguments(self, parser) -> None:
        parser.add_argument("order_ids", nargs="+", type=int)

    def handle(self, *args, **options) -> None:
        for order_id in options["order_ids"]:
            order = Order.objects.get(pk=order_id)
            dolyame = Dolyame(order=order)

            dolyame.refund()

            self.stdout.write(self.style.SUCCESS(f"Issued refund on order {order_id}"))
