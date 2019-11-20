from datetime import timedelta

from django.utils import timezone

from app.tasks import send_mail
from orders.models import Order
from triggers.base import BaseTrigger
from triggers.helpers import lower_first


class StartedPurchaseTrigger(BaseTrigger):
    name = 'started_purchase'
    template_id = 1090429

    PERIOD = timedelta(days=1)

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

    def send(self):
        send_mail.delay(
            template_id=self.template_id,
            to=self.order.user.email,
            ctx=self.get_template_context(),
        )

    def get_template_context(self):
        return {
            'item': self.order.item.full_name,
            'item_lower': lower_first(self.order.item.full_name),
            'firstname': self.order.user.first_name,
            'item_url': self.order.item.get_absolute_url(),
        }
