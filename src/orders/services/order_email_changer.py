from django.utils.functional import cached_property

from orders.models import Order
from users.creator import UserCreator


class OrderEmailChanger:
    def __init__(self, order: Order, email: str):
        self.order = order
        self.email = email

    def __call__(self):
        if self.was_shipped:
            self.order.unship()

        self.order.user = self.get_user()
        self.order.save()

        if self.was_shipped:
            self.order.ship()

    @cached_property
    def was_shipped(self) -> bool:
        return self.order.shipped is not None

    def get_user(self):
        return UserCreator(email=self.email, name='')()
