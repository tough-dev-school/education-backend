from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.services import BaseService
from banking.selector import get_bank
from orders.services import OrderCreator
from users.services import UserCreator

if TYPE_CHECKING:
    from orders.models import Order
    from products.models import Product
    from users.models import User


@dataclass
class PurchaseCreator(BaseService):
    """
    Entry point for creating purchase by user:
    - creates the user if necessary
    - creates order for chosen item
    - returns payment link for this order
    """

    item: "Product"
    name: str
    email: str
    subscribe: bool = False
    promocode: str | None = None
    desired_bank: str | None = None
    success_url: str | None = None
    redirect_url: str | None = None

    def act(self) -> str:
        user = self.create_user(self.name, self.email, self.subscribe)
        order = self.create_order(self.item, self.promocode, self.desired_bank, user)
        return self.get_payment_link(order, self.desired_bank, self.success_url, self.redirect_url)

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

    @staticmethod
    def get_payment_link(order: "Order", desired_bank: str | None, success_url: str | None, redirect_url: str | None) -> str:
        Bank = get_bank(desired=desired_bank)
        bank = Bank(
            order=order,
            redirect_url=redirect_url,
            success_url=success_url,
        )

        return bank.get_initial_payment_url()
