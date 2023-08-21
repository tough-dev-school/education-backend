from django.apps import apps
from django.core.management.base import BaseCommand

from amocrm.tasks import push_order_to_amocrm


class Command(BaseCommand):
    help = "Update not paid leads for users with b2b tag"

    def handle(self, *args, **kwargs):
        AmoCRMOrderLead = apps.get_model("amocrm.AmoCRMOrderLead")
        orders_ids_with_b2b_tag = (
            AmoCRMOrderLead.objects.filter(order__user__tags__contains=["b2b"], order__paid__isnull=True)
            .select_related("order", "order__user")
            .values_list("order_id", flat=True)
        )

        for order_id in orders_ids_with_b2b_tag:
            push_order_to_amocrm.delay(order_id=order_id)

        self.stdout.write(self.style.SUCCESS("Tasks for update orders has been successfully created."))
