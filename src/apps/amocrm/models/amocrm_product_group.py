from django.db import models

from core.models import TimestampedModel


class AmoCRMProductGroup(TimestampedModel):
    """
    Link model for products.models.Group and AmoCRM products catalog selectable field GROUP
    """

    group = models.OneToOneField("products.Group", on_delete=models.PROTECT, related_name="amocrm_group")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
