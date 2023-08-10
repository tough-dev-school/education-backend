from django.apps import apps
from django.core.management.base import BaseCommand
from amocrm.tasks import push_order_to_amocrm


class Command(BaseCommand):
    help = "Export orders to AmoCRM"

    def handle(self, *args, **kwargs):
        Order = apps.get_model("orders.Order")

        orders_ids = Order.objects.all().values_list("id", flat=True)
        for order_id in orders_ids:
            push_order_to_amocrm.delay(order_id=order_id)

        self.stdout.write(self.style.SUCCESS(f"Tasks for exporting orders has been successfully created."))
