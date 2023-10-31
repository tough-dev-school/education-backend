from django.db import models

from core.models import TimestampedModel


class AmoCRMOrderTransaction(TimestampedModel):
    """
    Link model for Order and AmoCRM customer's transaction
    """

    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
