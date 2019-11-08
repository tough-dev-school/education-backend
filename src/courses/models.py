from django.utils.translation import ugettext_lazy as _

from app.models import TimestampedModel, models
from app.s3 import AppS3


class Course(TimestampedModel):
    name = models.CharField(max_length=255)
    name_genitive = models.CharField(_('Genitive name'), max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ['-id']


class Record(TimestampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    s3_object_id = models.CharField(max_length=512)

    class Meta:
        ordering = ['-id']

    def get_url(self, expires: int = 3 * 24 * 60 * 60):
        return AppS3().get_presigned_url(self.s3_object_id, expires=expires)
