from datetime import datetime
from datetime import timedelta
from urllib.parse import urljoin
import uuid

from django.conf import settings
from django.utils import timezone

from core.models import models
from core.models import TimestampedModel


def default_expiration() -> datetime:
    return timezone.now() + timedelta(hours=2)


class PasswordlessAuthTokenQuerySet(models.QuerySet):
    def valid(self) -> "PasswordlessAuthTokenQuerySet":
        return self.filter(expires__gt=timezone.now(), used__isnull=True)


PasswordlessAuthTokenManager = models.Manager.from_queryset(PasswordlessAuthTokenQuerySet)


class PasswordlessAuthToken(TimestampedModel):
    objects = PasswordlessAuthTokenManager()

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    expires = models.DateTimeField(default=default_expiration)
    used = models.DateTimeField(null=True)

    def get_absolute_url(self) -> str:
        return urljoin(settings.FRONTEND_URL, "/".join(["auth", "passwordless", str(self.token), ""]))

    def mark_as_used(self) -> None:
        if not settings.DANGEROUSLY_MAKE_ONE_TIME_PASSWORDLESS_TOKEN_MULTI_PASS:
            self.used = timezone.now()
            self.save()
