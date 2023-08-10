from django.apps import apps
from django.core.management.base import BaseCommand
from amocrm.tasks import push_user_to_amocrm


class Command(BaseCommand):
    help = "Export users with orders to AmoCRM"

    def handle(self, *args, **kwargs):
        Order = apps.get_model("orders.Order")

        users_ids_with_orders = Order.objects.all().values_list("user_id", flat=True)
        for user_id in set(users_ids_with_orders):
            push_user_to_amocrm.delay(user_id=user_id)

        self.stdout.write(self.style.SUCCESS(f"Tasks for exporting users has been successfully created."))
