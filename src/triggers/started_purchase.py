from datetime import timedelta

from django.utils import timezone

from app.tasks import send_mail
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
            timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2

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
        }
