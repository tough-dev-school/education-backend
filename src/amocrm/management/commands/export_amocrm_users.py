from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Q

from amocrm.tasks import push_user_to_amocrm


class Command(BaseCommand):
    help = "Export users with orders to AmoCRM"

    def handle(self, *args, **kwargs):
        Order = apps.get_model("orders.Order")

        users_ids = (
            Order.objects.filter(~Q(user__email=""), unpaid__isnull=True, user__is_active=True, user__is_staff=False, user__email__isnull=False)
            .select_related("user")
            .values_list("user_id", flat=True)
        )
        for user_id in set(users_ids):
            push_user_to_amocrm.delay(user_id=user_id)

        self.stdout.write(self.style.SUCCESS("Tasks for exporting users has been successfully created."))
