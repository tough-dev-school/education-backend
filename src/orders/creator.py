from typing import Optional

from rest_framework import serializers

from orders.models import Order, PromoCode
from users.models import User


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'user',
            'price',
            'promocode',
        ]


class OrderCreator:
    def __init__(self, user: User, item, promocode=None, **kwargs):
        self.item = item
        self.data = {
            'user': user.pk,
            **kwargs,
            'price': item.get_price(promocode=promocode),
            'promocode': self._get_promocode_id(promocode_name=promocode),
        }

    def __call__(self) -> Order:
        order = self.create()

        order.set_item(self.item)
        order.save()

        return order

    def create(self):
        serializer = OrderCreateSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return serializer.instance

    def _get_promocode_id(self, promocode_name: str) -> Optional[int]:
        promocode = PromoCode.objects.get_or_nothing(name=promocode_name)

        if promocode is not None:
            return promocode.pk
