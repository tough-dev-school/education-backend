from datetime import timedelta

from django.utils import timezone

from orders.models import Order
from triggers.base import BaseTrigger


class StartedPurchaseTrigger(BaseTrigger):
    name = 'started_purchase'
    template_id = 'started-purchase'

    PERIOD = timedelta(days=1)

    def condition(self):
        """Order should not be paid and was created more then two days ago (safety)
        """
        return all([
            self.order.paid is None,
            self._is_created_recently(),
            self._customer_has_no_paid_orders_in_last_month(),
        ])

    def _is_created_recently(self) -> bool:
        return timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2

    def _customer_has_no_paid_orders_in_last_month(self) -> bool:
        return not Order.objects \
            .filter(user=self.order.user) \
            .filter(paid__isnull=False) \
            .filter(created__gte=timezone.now() - timedelta(weeks=5)) \
            .exclude(pk=self.order.pk) \
            .exists()
