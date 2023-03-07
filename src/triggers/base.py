from abc import ABCMeta
from abc import abstractmethod

from django.core.exceptions import ImproperlyConfigured

from app.helpers import lower_first
from mailing.tasks import send_mail
from orders.models import Order
from triggers.models import TriggerLogEntry


class BaseTrigger(metaclass=ABCMeta):
    name: str = ""
    template_id: str = ""

    def __init__(self, order: Order):
        if self.name is None:
            raise ImproperlyConfigured("Please set the name property")

        self.order = order

    def __call__(self) -> bool:
        if not self.should_be_sent():
            return False

        self.send()
        self.log_success()

        return True

    @abstractmethod
    def condition(self) -> bool:
        raise NotImplementedError("Please define in your trigger")

    def is_sent(self) -> bool:
        return (
            TriggerLogEntry.objects.filter(order=self.order, trigger=self.name).exists()
            or TriggerLogEntry.objects.filter(order__user__email=self.order.user.email, trigger=self.name).exists()
        )

    def should_be_sent(self) -> bool:
        if self.is_sent():
            return False

        return all(
            [
                self.message_does_not_look_like_a_message_that_should_never_be_sent(),
                self.condition(),  # defined in sub-class
            ]
        )

    def message_does_not_look_like_a_message_that_should_never_be_sent(self) -> bool:

        if self.order.course_id is not None:
            if self.order.course.disable_triggers is True:
                return False

        if self.order.giver is not None:
            return False

        return True

    def log_success(self) -> TriggerLogEntry:
        return TriggerLogEntry.objects.create(order=self.order, trigger=self.name)

    def send(self) -> None:
        send_mail.delay(
            template_id=self.template_id,
            to=self.order.user.email,
            ctx=self.get_template_context(),
        )

    def get_template_context(self) -> dict[str, str]:
        return {
            "item": self.order.item.full_name,
            "item_lower": lower_first(self.order.item.full_name),
            "firstname": self.order.user.first_name,
        }
