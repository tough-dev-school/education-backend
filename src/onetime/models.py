import uuid
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from app.models import DefaultQuerySet, TimestampedModel, models

EXPIRATION_TIME = timedelta(days=2)


class TokenQuerySet(DefaultQuerySet):
    def active(self):
        return self.filter(
            Q(expires__isnull=True) | Q(expires__gt=timezone.now()),
        )


class Token(TimestampedModel):

    objects = TokenQuerySet.as_manager()  # type: TokenQuerySet

    token = models.CharField(max_length=36, default=uuid.uuid4, unique=True, db_index=True)
    record = models.ForeignKey('courses.Record', on_delete=models.CASCADE)
    expires = models.DateTimeField(blank=True, null=True)

    def download(self):
        self.expires = timezone.now() + EXPIRATION_TIME
        self.save()

        return self.record.get_url()
