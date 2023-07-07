from django.core.exceptions import ImproperlyConfigured


class EmptyOrderException(RuntimeError):
    """Order without an item"""


class UnknownItemException(ImproperlyConfigured):
    pass
