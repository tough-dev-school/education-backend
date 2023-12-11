from decimal import Decimal
import random
from typing import Any

from apps.orders.models import Order
from apps.products.models import Product
from apps.users.models import User
from core.helpers import random_string
from core.test.factory import register


@register
def order(
    self: Any,
    slug: str | None = None,
    is_paid: bool = False,
    item: Product | None = None,
    user: User | None = None,
    author: User | None = None,
    price: Decimal | None = None,
    bank_id: str | None = "tinkoff_bank",
    **kwargs: dict[str, Any]
) -> Order:
    user = user if user else self.mixer.blend('users.User')
    price = price if price is not None else Decimal('%d.%d' % (random.randint(1, 100500), random.randint(0, 99)))
    course = item if item else self.course(price=price)

    order = self.mixer.blend(
        "orders.Order",
        slug=slug if slug else random_string(32),
        course=course,
        price=price,
        bank_id=bank_id,
        user=user,
        author=author if author else user,
    **kwargs)

    if is_paid:
        order.set_paid(silent=True)

    return order
