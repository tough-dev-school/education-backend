
from functools import partial
from mixer.backend.django import mixer


def register(method):
    name = method.__name__
    FixtureRegistry.METHODS[name] = method
    return method


class FixtureRegistry:
    METHODS = {}

    def get(self, name):
        method = self.METHODS.get(name)
        if not method:
            raise AttributeError(f'Factory method “{name}” not found.')
        return method


class CycleFixtureFactory:
    def __init__(self, factory, count: int):
        self.factory = factory
        self.count = count

    def __getattr__(self, name):
        if hasattr(self.factory, name):
            return lambda *args, **kwargs: [getattr(self.factory, name)(*args, **kwargs) for _ in range(0, self.count)]


class FixtureFactory:
    def __init__(self):
        self.mixer = mixer
        self.registry = FixtureRegistry()

    def __getattr__(self, name):
        method = self.registry.get(name)
        return partial(method, self)

    def cycle(self, count) -> CycleFixtureFactory:
        """
        Run given method X times:
            factory.cycle(5).order()  # gives 5 orders
        """
        return CycleFixtureFactory(self, count)
