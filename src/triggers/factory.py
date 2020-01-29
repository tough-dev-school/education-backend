_registry = dict()

__all__ = [
    'get_all_triggers',
    'register',
    'run',
]


class TriggerAlgoritmNotFound(Exception):
    pass


def register(trigger_name):
    def decorator(cls):
        cls.name = trigger_name
        _registry[trigger_name] = cls

        return cls

    return decorator


def get(trigger_name):
    cls = _registry.get(trigger_name)
    if not cls:
        raise TriggerNotRegistered(f'Trigger {trigger_name} not defined')

    return cls


def run(trigger_name, order):
    Triger = get(trigger_name)

    return Triger(order)()


def get_all_triggers():
    return _registry.values()
