from datetime import timedelta

from django.utils import timezone

from orders.models import Order
from triggers.base import BaseTrigger
from triggers.factory import register

@register('started_purchase')
class StartedPurchaseTrigger(BaseTrigger):
    template_id = 1090429

    PERIOD = timedelta(days=1)

    @classmethod
    def find_orders(cls):
        orders = Order.objects.filter(paid__isnull=True, created__gte=timezone.now() - timedelta(days=3))

        return orders.values_list('pk', flat=True).iterator()

    def condition(self):
        """Order should not be paid and was created more then two days ago (safety)
        """
        return self.order.paid is None and \
            self._is_created_recently() and \
            self._customer_has_no_paid_orders_in_last_month()

    def _is_created_recently(self) -> bool:
        return timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2

    def _customer_has_no_paid_orders_in_last_month(self) -> bool:
        return not Order.objects \
            .filter(user=self.order.user) \
            .filter(paid__isnull=False) \
            .filter(created__gte=timezone.now() - timedelta(weeks=5)) \
            .exclude(pk=self.order.pk) \
            .exists()
