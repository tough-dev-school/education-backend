from typing import Any

from app.test.factory import register
from orders.models import Order
from products.models import Product


@register
def order(self: Any, is_paid: bool = False, item: Product | None = None, **kwargs: dict[str, Any]) -> Order:
    order = self.mixer.blend("orders.Order", **kwargs)

    if item is not None:
        order.set_item(item)

        if "price" not in kwargs:
            order.price = item.price

        order.save()

    if is_paid:
        order.set_paid()

    return order
