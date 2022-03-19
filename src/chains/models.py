from typing import Optional

from datetime import timedelta
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel, models
from studying.models import Study


class ChainQuerySet(QuerySet):
    def active(self) -> QuerySet['Chain']:
        return self.filter(sending_is_active=True)

    def editable(self) -> QuerySet['Chain']:
        return self.filter(
            sending_is_active=False,
        ).select_related(
            'course',
        )


class Chain(TimestampedModel):
    objects = models.Manager.from_queryset(ChainQuerySet)()

    name = models.CharField(_('Name'), max_length=256)
    course = models.ForeignKey('products.Course', verbose_name=_('Course'), on_delete=models.CASCADE)

    sending_is_active = models.BooleanField(_('Sending is active'), default=False)

    class Meta:
        verbose_name = _('Email chain')
        verbose_name_plural = _('Email chains')
        constraints = [
            models.UniqueConstraint(fields=['name', 'course'], name='unique_name_per_course'),
        ]

    def __str__(self) -> str:
        return self.name


class MessageQuerySet(QuerySet):
    def may_be_parent(self) -> QuerySet['Message']:
        return self.filter(
            chain__sending_is_active=False,
            children__isnull=True,
        ).select_related(
            'chain',
            'chain__course',
        )


class Message(TimestampedModel):
    objects = models.Manager.from_queryset(MessageQuerySet)()

    name = models.CharField(_('Name'), max_length=256)
    chain = models.ForeignKey('chains.Chain', verbose_name=_('Chain'), on_delete=models.CASCADE)
    template_id = models.CharField(_('Template id'), max_length=256)

    parent = models.ForeignKey('chains.Message', on_delete=models.PROTECT, verbose_name=_('Parent'), related_name='children', null=True, blank=True, help_text=_('Messages without parent will be sent upon start'))

    delay = models.BigIntegerField(_('Delay (minutes)'), default=0, help_text=_('86400 for day, 604800 for week'))

    class Meta:
        verbose_name = _('Email chain message')
        verbose_name_plural = _('Email chain messages')
        constraints = [
            models.UniqueConstraint(fields=['name', 'chain'], name='unique_name_per_chain'),
        ]

    def __str__(self) -> str:
        return f'{self.chain.course}, {self.chain} {self.name}'

    def time_to_send(self, study: Study) -> bool:
        if self.parent is None:
            return False

        previous_message_progress = Progress.objects.filter(study=study, message=self.parent).first()

        if previous_message_progress is None:
            return False

        return timezone.now() - previous_message_progress.created > timedelta(minutes=self.delay)


class ProgressQuerySet(models.QuerySet):
    def get_last_progress(self, chain: Chain, study: Study) -> Optional['Progress']:
        return self.filter(study=study, message__chain=chain).order_by('-created').first()


class Progress(TimestampedModel):
    objects = models.Manager.from_queryset(ProgressQuerySet)()

    study = models.ForeignKey('studying.Study', on_delete=models.CASCADE)
    message = models.ForeignKey('chains.Message', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['study', 'message'], name='single_message_per_study'),
        ]

        indexes = [
            models.Index(fields=['study', 'message']),
        ]
