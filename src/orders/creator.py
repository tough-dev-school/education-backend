from rest_framework import serializers

from orders.models import Order
from users.models import User


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'user',
            'price',
        ]


class OrderCreator:
    def __init__(self, user: User, item, **kwargs):
        self.item = item
        self.data = {
            'user': user.pk,
            **kwargs,
            'price': item.get_price(),
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
