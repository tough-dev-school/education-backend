from dataclasses import dataclass

from celery import chain

from apps.amocrm.tasks import amocrm_enabled
from apps.amocrm.tasks import push_order
from apps.amocrm.tasks import push_user
from apps.banking.selector import get_bank_or_default
from apps.banking.zero_price_bank import ZeroPriceBank
from apps.orders.models import Order
from apps.orders.services import OrderCreator
from apps.products.models import Product
from apps.users.models import User
from apps.users.services import UserCreator
from apps.users.tasks import rebuild_tags
from core.services import BaseService


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
        )
        order = self.create_order(
            item=self.item,
            promocode=self.promocode,
            desired_bank=self.desired_bank,
            user=user,
        )

        self.after_creation(order=order)

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
            push_to_amocrm=False,
        )
        return creator()

    @staticmethod
    def get_or_create_user(name: str, email: str) -> User:
        return UserCreator(
            name=name,
            email=email.strip(),
            push_to_amocrm=False,
        )()

    @staticmethod
    def get_payment_link(order: Order, desired_bank: str | None, success_url: str | None, redirect_url: str | None) -> str:
        Bank = get_bank_or_default(desired=desired_bank)
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

    def after_creation(self, order: Order) -> None:
        if amocrm_enabled():
            chain(
                rebuild_tags.si(student_id=order.user.id, subscribe=self.subscribe),
                push_user.si(user_id=order.user.id),
                push_order.si(order_id=order.id),
            ).delay()
