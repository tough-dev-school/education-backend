from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services import BaseService
from orders.services import OrderCreator
from users.services import UserCreator

if TYPE_CHECKING:
    from orders.models import Order
    from products.models import Product
    from users.models import User


@dataclass
class PurchaseCreator(BaseService):
    item: "Product"
    name: str
    email: str
    subscribe: bool = False
    promocode: str | None = None
    desired_bank: str | None = None

    def act(self) -> "Order":
        user = self.create_user(self.name, self.email, self.subscribe)
        return self.create_order(self.item, self.promocode, self.desired_bank, user)

    @staticmethod
    def create_order(item: "Product", promocode: str | None, desired_bank: str | None, user: "User") -> "Order":
        creator = OrderCreator(
            user=user,
            item=item,
            promocode=promocode,
            desired_bank=desired_bank,
        )
        return creator()

    @staticmethod
    def create_user(name: str, email: str, subscribe: bool = False) -> "User":
        return UserCreator(
            name=name,
            email=email.strip(),
            subscribe=subscribe,
        )()
