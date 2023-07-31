from dataclasses import dataclass

from app.services import BaseService
from banking.selector import get_bank
from banking.zero_price_bank import ZeroPriceBank
from orders.models import Order
from orders.services import OrderCreator
from products.models import Product
from users.models import User
from users.services import UserCreator


@dataclass
class PurchaseCreator(BaseService):
    """
    Entry point for creating purchase by user:
    - creates the user if necessary
    - creates the order with given item
    - returns payment link for this order
    """

    item: Product
    user_name: str
    email: str
    subscribe: bool = False
    promocode: str | None = None
    desired_bank: str | None = None
    success_url: str | None = None
    redirect_url: str | None = None

    def act(self) -> str:
        user = self.get_or_create_user(
            name=self.user_name,
            email=self.email,
            subscribe=self.subscribe,
        )
        order = self.create_order(
            item=self.item,
            promocode=self.promocode,
            desired_bank=self.desired_bank,
            user=user,
        )
        return self.get_payment_link(
            order=order,
            desired_bank=self.desired_bank,
            success_url=self.success_url,
            redirect_url=self.redirect_url,
        )

    @staticmethod
    def create_order(item: Product, promocode: str | None, desired_bank: str | None, user: User) -> Order:
        creator = OrderCreator(
            user=user,
            item=item,
            promocode=promocode,
            desired_bank=desired_bank,
        )
        return creator()

    @staticmethod
    def get_or_create_user(name: str, email: str, subscribe: bool = False) -> User:
        return UserCreator(
            name=name,
            email=email.strip(),
            subscribe=subscribe,
        )()

    @staticmethod
    def get_payment_link(order: Order, desired_bank: str | None, success_url: str | None, redirect_url: str | None) -> str:
        Bank = get_bank(desired=desired_bank)
        if Bank is ZeroPriceBank:
            bank = Bank(
                order=order,
                success_url=success_url,
                redirect_url=redirect_url,  # type: ignore
            )
        else:
            bank = Bank(
                order=order,
                success_url=success_url,
            )

        return bank.get_initial_payment_url()
