from collections.abc import Callable
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from apps.orders.models import Order
    from apps.products.models import Product, ProductType
    from apps.studying.shipment.base import BaseShipment
    from apps.users.models import User

_registry: dict["ProductType", Type["BaseShipment"]] = {}

__all__ = [
    "register",
    "ship",
]


class ShipmentAlgorithmNotFound(Exception):
    pass


def register(model: "ProductType") -> Callable[[Type["BaseShipment"]], Type["BaseShipment"]]:
    def decorator(klass: Type["BaseShipment"]) -> Type["BaseShipment"]:
        _registry[model] = klass

        return klass

    return decorator


def get(item: "Product") -> Type["BaseShipment"]:
    klass = _registry.get(item.__class__)
    if not klass:
        raise ShipmentAlgorithmNotFound(f"Shipment alogorithm for {item} ({item.__class__}) not found.")

    return klass


def ship(item: "Product", to: "User", order: "Order") -> None:
    Shipment = get(item)

    Shipment(user=to, product=item, order=order)()


def unship(order: "Order") -> None:
    Shipment = get(order.item)

    Shipment(user=order.user, product=order.item, order=order).unship()
