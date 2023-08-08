from django.db import models

from app.models import TimestampedModel


class AmoCRMOrderTransaction(TimestampedModel):
    """
    Link model for Order and AmoCRM customer's transaction
    """

    order = models.OneToOneField("orders.Order", on_delete=models.PROTECT, related_name="amocrm_transaction")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
