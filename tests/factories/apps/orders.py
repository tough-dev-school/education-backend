from typing import Any

from core.helpers import random_string
from core.test.factory import register
from apps.orders.models import Order
from apps.products.models import Product


@register
def order(self: Any, slug: str | None = None, is_paid: bool = False, item: Product | None = None, **kwargs: dict[str, Any]) -> Order:
    slug = slug if slug else random_string(32)
    order = self.mixer.blend("orders.Order", slug=slug, **kwargs)

    if item is not None:
        order.set_item(item)

        if "price" not in kwargs:
            order.price = item.price

        order.save()

    if "bank_id" not in kwargs:
        order.update(bank_id="tinkoff_bank")

    if is_paid:
        order.set_paid()

    return order
