from django.db import models

from core.models import TimestampedModel


class AmoCRMOrderLead(TimestampedModel):
    """
    Link model for Order and AmoCRM amocrm_lead
    """

    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
