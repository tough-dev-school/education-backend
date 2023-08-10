from datetime import timedelta

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from amocrm.tasks import push_order_to_amocrm


class Command(BaseCommand):
    help = "Export orders with courses to AmoCRM"

    def handle(self, *args, **kwargs):
        Order = apps.get_model("orders.Order")
        three_months_ago = timezone.now() - timedelta(days=90)

        paid_orders_ids = (
            Order.objects.filter(
                ~Q(user__email=""),
                unpaid__isnull=True,
                user__is_active=True,
                user__is_staff=False,
                user__email__isnull=False,
                paid__isnull=False,
                course__isnull=False,
            )
            .select_related("user")
            .values_list("id", flat=True)
        )
        started_orders_ids = (
            Order.objects.filter(
                ~Q(user__email=""),
                unpaid__isnull=True,
                user__is_active=True,
                user__is_staff=False,
                user__email__isnull=False,
                paid__isnull=True,
                created__gte=three_months_ago,
                course__isnull=False,
            )
            .select_related("user")
            .values_list("id", flat=True)
        )
        orders_ids = {*paid_orders_ids, *started_orders_ids}
        for order_id in orders_ids:
            push_order_to_amocrm.delay(order_id=order_id)

        self.stdout.write(self.style.SUCCESS("Tasks for exporting orders has been successfully created."))
