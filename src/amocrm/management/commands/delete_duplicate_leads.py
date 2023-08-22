from django.apps import apps
from django.core.management.base import BaseCommand

from amocrm.tasks import delete_order_from_amocrm


class Command(BaseCommand):
    help = "Delete duplicated leads from amocrm"

    def handle(self, *args, **kwargs):
        AmoCRMOrderLead = apps.get_model("amocrm.AmoCRMOrderLead")
        Order = apps.get_model("orders.Order")

        leads = AmoCRMOrderLead.objects.all()
        duplicated_orders_ids = set()
        for lead in leads:
            course = lead.order.course
            user = lead.order.user
            orders_with_same_user_and_course = Order.objects.filter(user=user, course=course).order_by("created")
            finished_order = Order.objects.filter(user=user, course=course, paid__isnull=False, unpaid__isnull=True).last()

            duplicated_orders_ids.update(self.get_duplicated_orders_ids_with_lead(orders_with_same_user_and_course, finished_order))

        for order_id in duplicated_orders_ids:
            delete_order_from_amocrm.delay(order_id=order_id)

        self.stdout.write(self.style.SUCCESS(f"{len(duplicated_orders_ids)} Tasks for delete duplicated leads have been successfully created."))

    @staticmethod
    def get_duplicated_orders_ids_with_lead(orders_with_same_user_and_course, finished_order) -> list:
        if len(orders_with_same_user_and_course) > 1:
            if finished_order is not None:
                return [order.id for order in orders_with_same_user_and_course if order.id != finished_order.id and hasattr(order, "amocrm_lead")]
            else:
                duplicated_orders_ids_with_lead = [order.id for order in orders_with_same_user_and_course if hasattr(order, "amocrm_lead")]
                duplicated_orders_ids_with_lead.pop()
                return duplicated_orders_ids_with_lead
        return []
