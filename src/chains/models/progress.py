from typing import TYPE_CHECKING, Optional

from app.models import TimestampedModel, models
from studying.models import Study

if TYPE_CHECKING:
    from chains.models.chain import Chain


class ProgressQuerySet(models.QuerySet):
    def get_last_progress(self, chain: 'Chain', study: Study) -> Optional['Progress']:
        return self.filter(study=study, message__chain=chain).order_by('-created').first()


class Progress(TimestampedModel):
    objects = models.Manager.from_queryset(ProgressQuerySet)()

    study = models.ForeignKey('studying.Study', on_delete=models.CASCADE)
    message = models.ForeignKey('chains.Message', on_delete=models.CASCADE)
    success = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['study', 'message'], name='single_message_per_study'),
        ]

        indexes = [
            models.Index(fields=['study', 'message']),
        ]

    def __str__(self) -> str:
        return f'{self.study.student.email} {self.message.template_id}'


__all__ = [
    'Progress',
]
