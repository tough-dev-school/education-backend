from typing import Optional, Union

from datetime import datetime
from django_currentuser.middleware import get_current_authenticated_user

from orders.models import Order, PromoCode
from users.models import User


class OrderCreator:
    def __init__(
        self,
        user: User,
        item,
        promocode: Optional[str] = None,
        giver: User = None,
        desired_shipment_date: Optional[Union[str, datetime]] = None,
        gift_message: Optional[str] = None,
        desired_bank: Optional[str] = None,
    ):
        self.item = item
        self.user = user
        self.price = item.get_price(promocode=promocode)
        self.promocode = self._get_promocode(promocode)
        self.giver = giver
        self.desired_shipment_date = desired_shipment_date
        self.gift_message = gift_message if gift_message is not None else ''
        self.desired_bank = desired_bank if desired_bank is not None else ''

    def __call__(self) -> Order:
        order = self.create()

        order.set_item(self.item)
        order.save()

        return order

    def create(self):
        return Order.objects.create(
            user=self.user,
            author=get_current_authenticated_user() or self.user,
            price=self.price,
            promocode=self.promocode,
            giver=self.giver,
            desired_shipment_date=self.desired_shipment_date,
            gift_message=self.gift_message,
            desired_bank=self.desired_bank,
        )

    def _get_promocode(self, promocode_name: str) -> Optional[PromoCode]:
        return PromoCode.objects.get_or_nothing(name=promocode_name)
