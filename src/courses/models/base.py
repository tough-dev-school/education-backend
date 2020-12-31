from typing import Optional

from decimal import Decimal
from django.apps import apps
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models
from app.pricing import format_old_price, format_price
from orders.models import Order
from shipping import factory as ShippingFactory
from users.models import User


class Shippable(TimestampedModel):
    """Add this to every shippable item"""
    name = models.CharField(max_length=255)
    name_receipt = models.CharField(_('Name for receipts'), max_length=255, help_text='«посещение мастер-класса по TDD» или «Доступ к записи курсов кройки и шитья»')
    full_name = models.CharField(
        _('Full name for letters'), max_length=255,
        help_text='Билет на мастер-класс о TDD или «запись курсов кройки и шитья»',
    )
    slug = models.SlugField()

    price = models.DecimalField(max_digits=8, decimal_places=2)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        abstract = True

    def get_price_display(self):
        return format_price(self.price)

    def get_old_price_display(self):
        return format_price(self.old_price)

    def get_formatted_price_display(self):
        return format_old_price(self.old_price, self.price)

    def ship(self, to: User, order: Optional[Order] = None):
        return ShippingFactory.ship(self, to=to, order=order)

    def get_price(self, promocode=None) -> Decimal:
        promocode = apps.get_model('orders.PromoCode').objects.get_or_nothing(name=promocode)

        if promocode is not None:
            return promocode.apply(self.price)

        return self.price

    def get_template_id(self):
        """Get custom per-item template_id"""
        if not hasattr(self, 'template_id'):
            return

        if self.template_id is not None and len(self.template_id):
            return self.template_id
