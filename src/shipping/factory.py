_registry = dict()

__all__ = [
    'register',
    'ship',
]


class ShipmentAlgorithmNotFound(Exception):
    pass


def register(model):
    def decorator(klass):
        _registry[model] = klass

        return klass

    return decorator


def get(item):
    klass = _registry.get(item.__class__)
    if not klass:
        raise ShipmentAlgorithmNotFound(f'Shipment alogorithm for {item} ({item.__class__}) not found.')

    return klass


def ship(item, to, order=None):
    Shipment = get(item)

    return Shipment(user=to, product=item, order=order)()
