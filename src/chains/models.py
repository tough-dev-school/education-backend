from typing import Optional

from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models
from studying.models import Study


class Chain(TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)


class Message(TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    chain = models.ForeignKey('chains.Chain', on_delete=models.CASCADE)
    template_id = models.CharField(max_length=256)

    parent = models.ForeignKey('chains.Message', on_delete=models.SET_NULL, null=True)
    delay = models.BigIntegerField(_('Delay (minutes)'), default=0)

    def send(self, to: Study) -> None:
        Progress.objects.create(study=to, message=self)

    def time_to_send(self, to: Study) -> bool:
        if self.parent is None:
            return False

        previous_message_progress = Progress.objects.filter(study=to, message=self.parent).first()

        if previous_message_progress is None:
            return False

        return timezone.now() - previous_message_progress.created > timedelta(minutes=self.delay)


class ProgressQuerySet(models.QuerySet):
    def get_last_progress(self, chain: Chain, study: Study) -> Optional['Progress']:
        return Progress.objects.filter(study=study, message__chain=chain).order_by('-created').first()


class Progress(TimestampedModel):
    objects = models.Manager.from_queryset(ProgressQuerySet)()

    study = models.ForeignKey('studying.Study', on_delete=models.CASCADE)
    message = models.ForeignKey('chains.Message', on_delete=models.CASCADE)
