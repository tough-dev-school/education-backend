from abc import ABCMeta
from abc import abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.orders.models import Order
    from apps.products.models import Course
    from apps.users.models import User


class BaseShipment(metaclass=ABCMeta):
    template_id: str = ""

    def __init__(self, *, user: "User", product: "Course", order: "Order"):
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
