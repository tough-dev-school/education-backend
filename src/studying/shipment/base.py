from abc import ABCMeta
from abc import abstractmethod

from orders.models import Order
from products.models import Bundle
from products.models import Course
from products.models import Record
from users.models import User


class BaseShipment(metaclass=ABCMeta):
    template_id: str = ""

    def __init__(self, *, user: User, product: Course | Record | Bundle, order: Order):
        self.stuff_to_ship = product
        self.user = user
        self.order = order

    def __call__(self) -> None:
        self.ship()

    @abstractmethod
    def ship(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def unship(self) -> None:
        raise NotImplementedError()
