from datetime import timedelta

from django.utils import timezone

from orders.models import Order
from triggers.base import BaseTrigger
from triggers.factory import register
from triggers.tasks import run_trigger


@register('record_feedback')
class RecordFeedbackTrigger(BaseTrigger):

    template_id = 1167476
    PERIOD = timedelta(days=3)

    @classmethod
    def run(cls):
        for order in Order.objects.filter(paid__isnull=False, record__isnull=False, created__gte=timezone.now() - timedelta(days=6)).iterator():
            run_trigger.delay(cls.name, order.pk)

    def condition(self):
        """Order should be paid, item should be a record and was created more then three days ago
        """
        return self.order.paid is not None and \
            self._is_created_recently() and \
            self.order.record is not None

    def _is_created_recently(self) -> bool:
        return timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2
