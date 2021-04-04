import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from urllib.parse import urljoin

from app.models import TimestampedModel, models


def default_expiration():
    return timezone.now() + timedelta(hours=2)


class PasswordlessAuthToken(TimestampedModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    expires = models.DateTimeField(default=default_expiration)
    used = models.BooleanField(default=False)

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['auth', 'passwordless', str(self.token), '']))
