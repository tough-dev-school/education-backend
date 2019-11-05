from app.models import TimestampedModel, models


class ItemField(models.ForeignKey):
    """This is a simple replacement for the ContentType framework -- fields of this type
    are fields linked to items
    """
    def __init__(self, *args, **kwargs):
        self._is_item = True
        super().__init__(*args, **kwargs)


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
