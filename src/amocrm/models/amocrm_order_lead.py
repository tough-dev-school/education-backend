from django.db import models

from app.models import TimestampedModel


class AmoCRMOrderLead(TimestampedModel):
    """
    Link model for Order and AmoCRM amocrm_lead
    """

    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="amocrm_lead")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
