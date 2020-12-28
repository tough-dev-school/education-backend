import uuid
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

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

    class Meta:
        verbose_name = _('Onetime token')
        verbose_name_plural = _('Onetime tokens')

    def __str__(self):
        return str(self.token)

    def download(self):
        self.expires = timezone.now() + EXPIRATION_TIME
        self.save()

        return self.record.get_url()
