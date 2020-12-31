from typing import Optional, Union

from abc import ABCMeta, abstractmethod

from courses.models import Bundle, Course, Record
from orders.models import Order
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
