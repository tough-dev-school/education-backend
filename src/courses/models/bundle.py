from django.conf import settings
from django.utils.translation import gettext_lazy as _
from urllib.parse import urljoin

from app.models import models
from courses.models.base import Shippable


class Bundle(Shippable):
    records = models.ManyToManyField('courses.Record')
    courses = models.ManyToManyField('courses.Course')

    class Meta:
        ordering = ['-id']
        verbose_name = _('Bundle')
        verbose_name_plural = _('Bundles')

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['bundles', self.slug, '']))

    def ship(self, to):
        for record in self.records.iterator():
            record.ship(to=to)

        for course in self.courses.iterator():
            course.ship(to=to)
