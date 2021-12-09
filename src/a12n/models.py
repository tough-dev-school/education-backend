import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from urllib.parse import urljoin

from app.models import TimestampedModel, models


def default_expiration():
    return timezone.now() + timedelta(hours=2)


class PasswordlessAuthTokenQuerySet(models.QuerySet):
    def valid(self):
        return self.filter(expires__gt=timezone.now(), used__isnull=True)


class PasswordlessAuthToken(TimestampedModel):
    objects = models.Manager.from_queryset(PasswordlessAuthTokenQuerySet)()

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    expires = models.DateTimeField(default=default_expiration)
    used = models.DateTimeField(null=True)

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['auth', 'passwordless', str(self.token), '']))

    def mark_as_used(self):
        if not settings.DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS:
            self.used = timezone.now()
            self.save()
