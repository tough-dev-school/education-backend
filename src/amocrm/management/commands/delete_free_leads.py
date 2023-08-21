from django.apps import apps
from django.core.management.base import BaseCommand

from amocrm.tasks import delete_order_from_amocrm


class Command(BaseCommand):
    help = "Delete free leads and transactions from amocrm"

    def handle(self, *args, **kwargs):
        AmoCRMOrderLead = apps.get_model("amocrm.AmoCRMOrderLead")
        orders_ids_with_b2b_tag = AmoCRMOrderLead.objects.filter(order__price=0).select_related("order").values_list("order_id", flat=True)

        for order_id in orders_ids_with_b2b_tag:
            delete_order_from_amocrm.delay(order_id=order_id)

        self.stdout.write(self.style.SUCCESS("Tasks for delete free orders have been successfully created."))
