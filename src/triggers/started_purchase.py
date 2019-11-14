from datetime import timedelta

from django.utils import timezone

from triggers.base import BaseTrigger


class StartedPurchaseTrigger(BaseTrigger):
    name = 'started_purchase'
    PERIOD = timedelta(days=1)

    def condition(self):
        """Order should not be paid and was created more then two days ago (safety)
        """
        return self.order.paid is None and \
            timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2

    def send(self):
        pass
