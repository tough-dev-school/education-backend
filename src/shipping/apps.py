from django.apps import AppConfig


class ShippingConfig(AppConfig):
    name = 'shipping'

    def ready(self):
        """Register all shipping algorithms for the factory"""
        import shipping.shipments  # noqa
