from typing import Optional

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from app.models import DefaultQuerySet, TimestampedModel, models
from orders.signals import order_got_shipped


class ItemField(models.ForeignKey):
    """This is a simple replacement for the ContentType framework -- fields of this type
    are fields linked to items
    """
    def __init__(self, *args, **kwargs):
        self._is_item = True
        super().__init__(*args, **kwargs)


class UnknownItemException(Exception):
    pass


class OrderQuerySet(DefaultQuerySet):
    def paid(self, invert=False):
        return self.filter(paid__isnull=invert)


class Order(TimestampedModel):
    objects = OrderQuerySet.as_manager()  # type: OrderQuerySet

    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=9, decimal_places=2)

    paid = models.DateTimeField(
        _('Date when order got paid'),
        null=True, blank=True,
        help_text=_('If set during creation, order automaticaly gets shipped'),
    )
    shipped = models.DateTimeField(_('Date when order was shipped'), null=True, blank=True)

    course = ItemField('courses.Course', null=True, blank=True, on_delete=models.PROTECT)
    record = ItemField('courses.Record', null=True, blank=True, on_delete=models.PROTECT)

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
    def get_item_foreignkey(cls, item) -> Optional[models.fields.Field]:
        """
        Given an item model, returns the ForeignKey to it"""
        for field in cls._meta.get_fields():
            if getattr(field, '_is_item', False):
                if field.related_model == item.__class__:
                    return field.name

    def set_item(self, item):
        foreign_key = self.__class__.get_item_foreignkey(item)
        if foreign_key is not None:
            setattr(self, foreign_key, item)
            return

        raise UnknownItemException('There is not foreignKey for {}'.format(item.__class__))

    def set_paid(self):
        is_already_paid = self.paid is not None

        self.paid = timezone.now()

        self.save()

        if not is_already_paid and self.item is not None:
            self.ship()

    def ship(self):
        """Ship the order. Better call it asynchronously"""
        self.item.ship(to=self.user)

        self.shipped = timezone.now()

        self.save()

        order_got_shipped.send(
            sender=self.__class__,
            order=self,
        )
