from datetime import timedelta

from django.utils import timezone

from app.tasks import send_mail
from triggers.base import BaseTrigger
from triggers.helpers import lower_first


class RecordPurchaseTrigger(BaseTrigger):
    name = 'purchase_record'
    template_id = 123456  # FIXME

    PERIOD = timedelta(days=3)

    def condition(self):
        """Order should be paid, item should be a record and was created more then three days ago
        """
        return self.order.paid is not None and \
            self._is_created_recently() and \
            self.order.record is not None

    def _is_created_recently(self) -> bool:
        return timezone.now() - self.PERIOD > self.order.created > timezone.now() - self.PERIOD * 2

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
