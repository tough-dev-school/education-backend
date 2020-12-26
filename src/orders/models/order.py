from typing import Iterable, Optional

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.models import DefaultQuerySet, TimestampedModel, models
from orders.fields import ItemField
from orders.signals import order_got_shipped


class UnknownItemException(Exception):
    pass


class OrderQuerySet(DefaultQuerySet):
    def paid(self, invert=False):
        return self.filter(paid__isnull=invert)


class Order(TimestampedModel):
    objects = OrderQuerySet.as_manager()  # type: OrderQuerySet

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    promocode = models.ForeignKey('orders.PromoCode', verbose_name=_('Promo Code'), blank=True, null=True, on_delete=models.PROTECT)

    paid = models.DateTimeField(
        _('Date when order got paid'),
        null=True, blank=True,
        help_text=_('If set during creation, order automaticaly gets shipped'),
    )
    shipped = models.DateTimeField(_('Date when order was shipped'), null=True, blank=True)

    course = ItemField('courses.Course', null=True, blank=True, on_delete=models.PROTECT)
    record = ItemField('courses.Record', null=True, blank=True, on_delete=models.PROTECT)
    bundle = ItemField('courses.Bundle', null=True, blank=True, on_delete=models.PROTECT)

    giver = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL, related_name='created_gifts')
    desired_shipment_date = models.DateTimeField(_('Date when the gift should be shipped'), null=True, blank=True)
    gift_message = models.TextField(default='')

    class Meta:
        ordering = ['-id']
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f'Order #{self.pk}'

    @property
    def item(self):
        """Find the attached item. Simple replacement for ContentType framework
        """
        for field in self.__class__._meta.get_fields():
            if getattr(field, '_is_item', False):
                if getattr(self, f'{field.name}_id', None) is not None:
                    return getattr(self, field.name)

    @classmethod
    def _iterate_items(cls) -> Iterable[models.fields.Field]:
        for field in cls._meta.get_fields():
            if getattr(field, '_is_item', False):
                yield field

    @classmethod
    def get_item_foreignkey(cls, item) -> Optional[models.fields.Field]:
        """
        Given an item model, returns the ForeignKey to it"""
        for field in cls._iterate_items():
            if field.related_model == item.__class__:
                return field.name

    def reset_items(self):
        for field in self._iterate_items():
            setattr(self, field.name, None)

    def set_item(self, item):
        foreign_key = self.__class__.get_item_foreignkey(item)
        if foreign_key is not None:
            self.reset_items()
            setattr(self, foreign_key, item)
            return

        raise UnknownItemException('There is not foreignKey for {}'.format(item.__class__))

    def set_paid(self, silent=False):
        from orders.services.order_is_paid_setter import Griphook
        Griphook(self, silent=silent)()

    def ship(self, silent: bool = False):
        """Ship the order. Better call it asynchronously"""
        self.item.ship(to=self.user)

        self.shipped = timezone.now()

        self.save()

        order_got_shipped.send(
            sender=self.__class__,
            order=self,
            silent=silent,
        )
