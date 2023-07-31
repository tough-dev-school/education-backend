from django.db import models

from app.models import TimestampedModel


class AmoCRMUser(TimestampedModel):
    user = models.OneToOneField("users.User", on_delete=models.PROTECT)
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
