from shipping import factory


class Shippable:
    """Add this to every shippable item"""
    def ship(self, to):
        return factory.ship(self, to=to)

    def get_template_id(self):
        """Get custom per-item template_id"""
        if not hasattr(self, 'template_id'):
            return

        if self.template_id is not None and len(self.template_id):
            return self.template_id
