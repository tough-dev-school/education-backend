from typing import Any

from app.helpers import random_string
from app.test.factory import register
from orders.models import Order
from products.models import Product


@register
def order(self: Any, slug: str | None = None, is_paid: bool = False, item: Product | None = None, **kwargs: dict[str, Any]) -> Order:
    slug = slug if slug else random_string(32)
    order = self.mixer.blend("orders.Order", slug=slug, **kwargs)

    if item is not None:
        order.set_item(item)

        if "price" not in kwargs:
            order.price = item.price

        order.save()

    if is_paid:
        order.set_paid()

    return order
