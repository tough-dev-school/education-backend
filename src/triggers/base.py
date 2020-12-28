from abc import ABCMeta, abstractmethod
from django.core.exceptions import ImproperlyConfigured

from app.tasks import send_mail
from triggers.helpers import lower_first
from triggers.models import TriggerLogEntry


class BaseTrigger(metaclass=ABCMeta):
    name = None

    def __init__(self, order):
        if self.name is None:
            raise ImproperlyConfigured('Please set the name property')

        self.order = order

    def __call__(self):
        if not self.should_be_sent():
            return False

        self.send()
        self.log_success()

    @abstractmethod
    def condition(self) -> bool:
        raise NotImplementedError('Please define in your trigger')

    def is_sent(self) -> bool:
        return TriggerLogEntry.objects.filter(order=self.order, trigger=self.name).exists() or \
            TriggerLogEntry.objects.filter(order__user__email=self.order.user.email, trigger=self.name).exists()

    def should_be_sent(self) -> bool:
        if self.is_sent():
            return False

        return all([
            self.message_does_not_look_like_a_message_that_should_never_be_sent(),
            self.condition(),  # defined in sub-class
        ])

    def message_does_not_look_like_a_message_that_should_never_be_sent(self) -> bool:
        return self.order.giver is None

    def log_success(self):
        return TriggerLogEntry.objects.create(order=self.order, trigger=self.name)

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
