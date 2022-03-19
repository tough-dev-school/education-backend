from typing import Optional

from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models
from studying.models import Study


class Chain(TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)

    sending_is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Email chain')
        verbose_name_plural = _('Email chains')

    def __str__(self) -> str:
        return f'{self.course} {self.name}'


class Message(TimestampedModel):
    name = models.CharField(max_length=256, unique=True)
    chain = models.ForeignKey('chains.Chain', on_delete=models.CASCADE)
    template_id = models.CharField(max_length=256)

    parent = models.ForeignKey('chains.Message', on_delete=models.PROTECT, related_name='children', null=True, blank=True, limit_choices_to={'chain__sending_is_active': False, 'children__isnull': True})

    delay = models.BigIntegerField(_('Delay (minutes)'), default=0)

    class Meta:
        verbose_name = _('Email chain message')
        verbose_name_plural = _('Email chain messages')

    def __str__(self) -> str:
        return f'{self.chain} {self.name}'

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
