from app.models import TimestampedModel, models


class Course(TimestampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField()


class Record(TimestampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    s3_object_id = models.CharField(max_length=512)
