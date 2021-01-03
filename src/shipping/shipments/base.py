from typing import Optional, Union

from abc import ABCMeta, abstractmethod

from orders.models import Order
from products.models import Bundle, Course, Record
from users.models import User


class BaseShipment(metaclass=ABCMeta):
    template_id = None

    def __init__(self, user: User, product: Union[Course, Record, Bundle], order: Optional[Order] = None):
        self.stuff_to_ship = product
        self.user = user
        self.order = order

    def __call__(self):
        self.ship()

    @abstractmethod
    def ship(self):
        raise NotImplementedError()

    def get_gift_template_context(self) -> dict:
        """Return a template context used for gift letters"""
        if self.order is None or self.order.giver is None:
            return {}

        return {
            'giver_name': str(self.order.giver),
            'gift_message': self.order.gift_message,
        }
