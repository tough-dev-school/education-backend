from decimal import Decimal
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import ValidationError

from banking.base import Bank
from orders.models import Order


class ZeroPriceBank(Bank):
    """Bank used for zero-priced orders, redirects user to URL provided by frontend
    """
    currency = 'KIS'
    currency_symbol = '💋'
    acquiring_percent = Decimal(0)
    name = 'Бесплатно'

    def validate_order(self, order: Order) -> None:
        if order.price != 0:
            raise ValidationError('ZeroPriceBank may be used only with zero-priced orders')

    def get_initial_payment_url(self) -> str:
        if self.request is None:
            raise ImproperlyConfigured('ZeroPriceBank may be used only with given request')

        if 'redirect_url' not in self.request.data:
            raise ValidationError('Please provide redirect_url when using ZeroPriceBank')

        return self.request.data['redirect_url']
