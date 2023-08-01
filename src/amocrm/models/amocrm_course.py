from django.db import models

from app.models import TimestampedModel


class AmoCRMCourse(TimestampedModel):
    course = models.OneToOneField("products.Course", on_delete=models.PROTECT, related_name="amocrm_course")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
