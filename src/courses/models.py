from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from app.models import TimestampedModel, models
from app.s3 import AppS3
from shipping.mixins import Shippable


class Course(Shippable, TimestampedModel):
    name = models.CharField(max_length=255)
    name_genitive = models.CharField(_('Genitive name'), max_length=255)
    name_receipt = models.CharField(_('Name for receipts'), max_length=255, help_text=_('Will be printed in receipts'))
    slug = models.SlugField()
    clickmeeting_room_url = models.URLField(_('Clickmeeting room URL'), null=True, blank=True, help_text=_('If set, every user who purcashes this course gets invited'))

    class Meta:
        ordering = ['-id']

    def get_absolute_url(self):
        return urljoin(settings.ABSOLUTE_HOST, '/'.join(['courses', self.slug, '']))


class Record(Shippable, TimestampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    name_receipt = models.CharField(_('Name for receipts'), max_length=255, help_text=_('Will be printed in receipts'))
    slug = models.SlugField()

    s3_object_id = models.CharField(max_length=512)

    class Meta:
        ordering = ['-id']

    @property
    def name_genitive(self):
        return self.course.name_genitive

    def get_url(self, expires: int = 3 * 24 * 60 * 60):
        return AppS3().get_presigned_url(self.s3_object_id, expires=expires)

    def __str__(self):
        return f'Запись {self.name_genitive}'

    def get_absolute_url(self):
        return self.course.get_absolute_url()
