from datetime import timedelta

from django.utils import timezone

from triggers.base import BaseTrigger


class RecordFeedbackTrigger(BaseTrigger):
    name = 'record_feedback'
    template_id = 'record-feedback'

    PERIOD = timedelta(days=3)

    def condition(self):
        """Order should be paid, item should be a record and was created more then three days ago
        """
        return self.order.paid is not None and \
            self._is_created_recently() and \
            self.order.record is not None

    def _is_created_recently(self) -> bool:
        return timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2
