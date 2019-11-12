from shipping import factory


class Shippable:
    """Add this to every shippable item"""
    def ship(self, to):
        return factory.ship(self, to=to)
