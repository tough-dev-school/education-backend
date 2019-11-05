from abc import ABCMeta, abstractmethod


class BaseShipment(metaclass=ABCMeta):
    def __init__(self, stuff):
        self.stuff_to_ship = stuff

    def __call__(self):
        self.ship()

    @abstractmethod
    def ship(self):
        raise NotImplementedError()
