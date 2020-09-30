from abc import ABCMeta, abstractmethod


class BaseShipment(metaclass=ABCMeta):
    template_id = None

    def __init__(self, user, stuff):
        self.stuff_to_ship = stuff
        self.user = user

    def __call__(self):
        self.ship()

    @abstractmethod
    def ship(self):
        raise NotImplementedError()
