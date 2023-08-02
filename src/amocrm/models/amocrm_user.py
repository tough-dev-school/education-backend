from django.db import models

from app.models import TimestampedModel


class AmoCRMUser(TimestampedModel):
    """
    Link model for User and AmoCRM customer
    """

    user = models.OneToOneField("users.User", on_delete=models.PROTECT, related_name="amocrm_user")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
