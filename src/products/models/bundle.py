from django.utils.translation import gettext_lazy as _

from app.models import models
from products.models.base import Shippable


class Bundle(Shippable):
    records = models.ManyToManyField('products.Record')
    courses = models.ManyToManyField('products.Course')

    class Meta:
        ordering = ['-id']
        verbose_name = _('Bundle')
        verbose_name_plural = _('Bundles')
        db_table = 'courses_bundle'

    def ship(self, *args, **kwargs):
        for record in self.records.iterator():
            record.ship(*args, **kwargs)

        for course in self.courses.iterator():
            course.ship(*args, **kwargs)

    def unship(self, *args, **kwargs):
        for record in self.records.iterator():
            record.unship(*args, **kwargs)

        for course in self.courses.iterator():
            course.unship(*args, **kwargs)
