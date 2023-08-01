from django.db import models

from app.models import TimestampedModel


class AmoCRMProductGroup(TimestampedModel):
    group = models.OneToOneField("products.Group", on_delete=models.PROTECT, related_name="amocrm_group")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
