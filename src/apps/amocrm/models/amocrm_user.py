from django.db import models

from core.models import TimestampedModel


class AmoCRMUser(TimestampedModel):
    """
    Link model for User and AmoCRM customer
    """

    user = models.OneToOneField("users.User", on_delete=models.PROTECT, related_name="amocrm_user")
    customer_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
    contact_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
