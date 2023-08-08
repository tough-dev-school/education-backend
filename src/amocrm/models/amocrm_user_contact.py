from django.db import models

from app.models import TimestampedModel


class AmoCRMUserContact(TimestampedModel):
    """
    Link model for User and AmoCRM contact
    """

    user = models.OneToOneField("users.User", on_delete=models.PROTECT, related_name="amocrm_user_contact")
    amocrm_id = models.PositiveIntegerField(null=False, blank=False, unique=True)
