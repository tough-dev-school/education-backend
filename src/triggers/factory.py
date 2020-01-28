_registry = dict()

__all__ = [
    'register',
    'run',
]


class TriggerAlgoritmNotFound(Exception):
    pass


def register(trigger_name):
    def decorator(klass):
        _registry[trigger_name] = klass

        return klass

    return decorator


def get(trigger_name):
    klass = _registry.get(trigger_name)
    if not klass:
        raise TriggerAlgoritmNotFound(f'Trigger {trigger_name} not defined')

    return klass


def run(trigger_name, order):
    Triger = get(trigger_name)

    return Triger(order)()


def get_all_triggers():
    return _registry.values()
