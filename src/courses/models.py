from app.models import TimestampedModel, models
from app.s3 import AppS3


class Course(TimestampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField()


class Record(TimestampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    s3_object_id = models.CharField(max_length=512)

    def get_url(self, expires: int = 60 * 60):
        return AppS3().get_presigned_url(self.s3_object_id, expires=expires)
