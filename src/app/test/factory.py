
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


class FixtureFactory:
    def __init__(self):
        self.mixer = mixer
        self.registry = FixtureRegistry()

    def __getattr__(self, name):
        method = self.registry.get(name)
        return partial(method, self)
