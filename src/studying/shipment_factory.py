from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from orders.models import Order
    from products.models import Product, ProductType
    from studying.shipment.base import BaseShipment
    from users.models import User

_registry: dict['Product', Type['BaseShipment']] = {}

__all__ = [
    'register',
    'ship',
]


class ShipmentAlgorithmNotFound(Exception):
    pass


def register(model: 'ProductType'):
    def decorator(klass):
        _registry[model] = klass

        return klass

    return decorator


def get(item: 'Product') -> Type['BaseShipment']:
    klass = _registry.get(item.__class__)  # type: ignore
    if not klass:
        raise ShipmentAlgorithmNotFound(f'Shipment alogorithm for {item} ({item.__class__}) not found.')

    return klass


def ship(item, to: 'User', order: 'Order') -> None:
    Shipment = get(item)

    Shipment(user=to, product=item, order=order)()


def unship(order: 'Order') -> None:
    Shipment = get(order.item)

    Shipment(user=order.user, product=order.item, order=order).unship()
