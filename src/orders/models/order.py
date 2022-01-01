from typing import Iterable, Optional

import operator
from django.db.models import CheckConstraint, Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy
from functools import reduce

from app.models import TimestampedModel, models
from orders.fields import ItemField
from products.models import Product


class UnknownItemException(Exception):
    pass


def only_one_or_zero_is_set(*fields: str) -> Q:
    constraints = []
    for field in fields:
        constraint = Q(
            **{
                f'{field}__isnull': False,
                **{f'{empty_field}__isnull': True for empty_field in fields if empty_field != field},
            },
        )
        constraints.append(constraint)

    all_fields_can_empty_constraint = Q(
        **{f'{field}__isnull': True for field in fields},
    )

    constraints.append(all_fields_can_empty_constraint)

    return Q(reduce(operator.or_, constraints))


class OrderQuerySet(QuerySet):
    def paid(self, invert: Optional[bool] = False) -> QuerySet['Order']:
        return self.filter(paid__isnull=invert)

    def shipped_without_payment(self) -> QuerySet['Order']:
        return self.paid(invert=True).filter(shipped__isnull=False)

    def to_ship(self) -> QuerySet['Order']:
        """Paid orders that may be shipped right now"""
        return self.paid().filter(shipped__isnull=True, desired_shipment_date__lte=timezone.now())


class Order(TimestampedModel):
    objects = models.Manager.from_queryset(OrderQuerySet)()

    author = models.ForeignKey('users.User', related_name='created_orders', verbose_name=_('Order author'), on_delete=models.PROTECT, editable=False)
    user = models.ForeignKey('users.Student', verbose_name=_('User'), on_delete=models.PROTECT)
    price = models.DecimalField(_('Price'), max_digits=9, decimal_places=2)
    promocode = models.ForeignKey('orders.PromoCode', verbose_name=_('Promo Code'), blank=True, null=True, on_delete=models.PROTECT)

    paid = models.DateTimeField(
        _('Date when order got paid'),
        null=True, blank=True,
        help_text=_('If set during creation, order automaticaly gets shipped'),
    )
    unpaid = models.DateTimeField(_('Date when order got unpaid'), null=True, blank=True)
    shipped = models.DateTimeField(_('Date when order was shipped'), null=True, blank=True)

    desired_bank = models.CharField(_('User-requested bank string'), blank=True, max_length=32)

    course = ItemField(to='products.Course', verbose_name=_('Course'), null=True, blank=True, on_delete=models.PROTECT)  # type: ignore
    record = ItemField(to='products.Record', verbose_name=_('Record'), null=True, blank=True, on_delete=models.PROTECT)  # type: ignore
    bundle = ItemField(to='products.Bundle', verbose_name=_('Bundle'), null=True, blank=True, on_delete=models.PROTECT)  # type: ignore

    giver = models.ForeignKey('users.User', verbose_name=_('Giver'), null=True, blank=True, on_delete=models.SET_NULL, related_name='created_gifts')
    desired_shipment_date = models.DateTimeField(_('Date when the gift should be shipped'), null=True, blank=True)
    gift_message = models.TextField(_('Gift message'), default='', blank=True)
    notification_to_giver_is_sent = models.BooleanField(default=False)

    class Meta:
        ordering = ['-id']
        verbose_name = pgettext_lazy('orders', 'Order')
        verbose_name_plural = pgettext_lazy('orders', 'Orders')

        permissions = [
            ('pay_order', _('May mark orders as paid')),
            ('unpay_order', _('May mark orders as unpaid')),
        ]

        constraints = [
            CheckConstraint(
                check=only_one_or_zero_is_set('course', 'record', 'bundle'),
                name='only_one_or_zero_item_type_is_allowed',
            ),
        ]

    def __str__(self) -> str:
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
                yield field  # type: ignore

    @classmethod
    def get_item_foreignkey(cls, item: Product) -> Optional[str]:
        """
        Given an item model, returns the ForeignKey to it"""
        for field in cls._iterate_items():
            if field.related_model == item.__class__:
                return field.name

    def reset_items(self) -> None:
        for field in self._iterate_items():
            setattr(self, field.name, None)

    def set_item(self, item: Product) -> None:
        if self.shipped is not None:  # some denormalization happens during shipping, so please do not break it!
            raise ValueError('Cannot change item for shipped order!')

        foreign_key = self.__class__.get_item_foreignkey(item)
        if foreign_key is not None:
            self.reset_items()
            setattr(self, foreign_key, item)
            return

        raise UnknownItemException(f'There is no foreignKey for {item.__class__}')

    def set_paid(self, silent: Optional[bool] = False) -> None:
        from orders.services import OrderPaidSetter
        OrderPaidSetter(self, silent=silent)()

    def set_not_paid(self) -> None:
        from orders.services import OrderUnpaidSetter
        OrderUnpaidSetter(self)()

    def ship(self, silent: Optional[bool] = False) -> None:
        from orders.services import OrderShipper
        OrderShipper(self, silent=silent)()

    def ship_without_payment(self) -> bool:
        if self.paid is None:
            self.ship(silent=True)
            return True

        return False

    def unship(self):
        from orders.services import OrderUnshipper
        OrderUnshipper(self)()
