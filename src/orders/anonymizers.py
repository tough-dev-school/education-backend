from hattori.base import BaseAnonymizer, faker
from random import randint

from orders.models import Order, PromoCode


class OrderAnonymizer(BaseAnonymizer):
    model = Order

    attributes = [
        ('gift_message', faker.paragraph),
        ('price', lambda: faker.pydecimal(left_digits=5, right_digits=2, positive=True)),
    ]


class PromoCodeAnonymizer(BaseAnonymizer):
    model = PromoCode

    attributes = [
        ('name', faker.pystr),
        ('comment', faker.sentence),
        ('discount_percent', lambda: randint(0, 50)),
    ]
