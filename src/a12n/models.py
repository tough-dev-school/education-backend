import uuid
from datetime import timedelta
from django.utils import timezone

from app.models import TimestampedModel, models


def default_expiration():
    return timezone.now() + timedelta(hours=2)


class PasswordlessAuthToken(TimestampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    expires = models.DateTimeField(default=default_expiration)
    used = models.BooleanField(default=False)
