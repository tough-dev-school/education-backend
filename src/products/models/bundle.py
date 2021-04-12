from django.conf import settings
from django.utils.translation import gettext_lazy as _
from urllib.parse import urljoin

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

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['bundles', self.slug, '']))

    def ship(self, *args, **kwargs):
        for record in self.records.iterator():
            record.ship(*args, **kwargs)

        for course in self.courses.iterator():
            course.ship(*args, **kwargs)
