from typing import Optional

from orders.models import Order, PromoCode
from users.models import User


class OrderCreator:
    def __init__(
        self,
        user: User,
        item,
        promocode: str = None,
    ):
        self.item = item
        self.user = user
        self.price = item.get_price(promocode=promocode)
        self.promocode = self._get_promocode(promocode)

    def __call__(self) -> Order:
        order = self.create()

        order.set_item(self.item)
        order.save()

        return order

    def create(self):
        return Order.objects.create(
            user=self.user,
            price=self.price,
            promocode=self.promocode,
        )

    def _get_promocode(self, promocode_name: str) -> Optional[PromoCode]:
        return PromoCode.objects.get_or_nothing(name=promocode_name)
