from typing import Optional

from app.models import TimestampedModel, models


class ItemField(models.ForeignKey):
    """This is a simple replacement for the ContentType framework -- fields of this type
    are fields linked to items
    """
    def __init__(self, *args, **kwargs):
        self._is_item = True
        super().__init__(*args, **kwargs)


class UnknownItemException(Exception):
    pass


class Order(TimestampedModel):
    user = models.ForeignKey('users.User', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    is_paid = models.BooleanField(default=False)

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
