from abc import ABCMeta, abstractmethod
from urllib.parse import urljoin

from django.conf import settings

from orders.models import Order


class Bank(metaclass=ABCMeta):
    def __init__(self, order: Order):
        self.order = order

    @abstractmethod
    def get_initial_payment_url(self):
        raise NotImplementedError()

    @property
    def success_url(self):
        return urljoin(settings.FRONTEND_URL, '/success/')

    @property
    def fail_url(self):
        return urljoin(settings.FRONTEND_URL, '/error/?code=banking')

    @property
    def price(self):
        return int(self.order.price * 100)

    @property
    def user(self):
        return self.order.user
