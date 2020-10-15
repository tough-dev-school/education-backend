from django.utils.translation import ugettext_lazy as _

from app.integrations.s3 import AppS3
from app.models import models
from courses.models.base import Shippable


class Record(Shippable):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)

    s3_object_id = models.CharField(max_length=512)
    template_id = models.CharField(_('Postmark template_id'), max_length=256, blank=True, null=True, help_text=_('Leave it blank for the default template'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Record')
        verbose_name_plural = _('Records')

    @property
    def name_genitive(self):
        return self.course.name_genitive

    def get_url(self, expires: int = 30 * 24 * 60 * 60):
        return AppS3().get_presigned_url(self.s3_object_id, expires=expires)

    def __str__(self):
        return f'Запись {self.name_genitive}'

    def get_absolute_url(self):
        return self.course.get_absolute_url()
