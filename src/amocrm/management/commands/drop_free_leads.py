from django.apps import apps
from django.core.management.base import BaseCommand

from amocrm.tasks import drop_free_order_amocrm


class Command(BaseCommand):
    help = "Drop free leads"

    def handle(self, *args, **kwargs):
        AmoCRMOrderLead = apps.get_model("amocrm.AmoCRMOrderLead")
        free_orders_ids = AmoCRMOrderLead.objects.filter(order__price=0).select_related("order").values_list("order_id", flat=True)

        for order_id in free_orders_ids:
            drop_free_order_amocrm.delay(order_id=order_id)

        self.stdout.write(self.style.SUCCESS("Tasks for drop orders has been successfully created."))
