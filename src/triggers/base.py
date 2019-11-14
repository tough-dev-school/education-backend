from abc import ABCMeta, abstractmethod

from django.core.exceptions import ImproperlyConfigured

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

        if self.send():
            self.log_success()

    @abstractmethod
    def condition(self) -> bool:
        raise NotImplementedError('Please define in your trigger')

    @abstractmethod
    def send(self) -> bool:
        raise NotImplementedError('Please define in your trigger')

    def is_sent(self) -> bool:
        return TriggerLogEntry.objects.filter(order=self.order, trigger=self.name).exists()

    def should_be_sent(self) -> bool:
        if self.is_sent():
            return False

        return self.condition()

    def log_success(self):
        return TriggerLogEntry.objects.create(order=self.order, trigger=self.name)
