import uuid
from django.utils.translation import gettext_lazy as _

from app.models import DefaultQuerySet, TimestampedModel, models


class DiplomaQuerySet(DefaultQuerySet):
    def for_viewset(self):
        return self.select_related('study', 'study__student', 'study__course')

    def for_user(self, user):
        return self.filter(study__student=user)


class Diploma(TimestampedModel):
    class Languages(models.TextChoices):
        RU = 'RU', _('Russian')
        EN = 'EN', _('English')

    objects: DiplomaQuerySet = DiplomaQuerySet.as_manager()

    study = models.ForeignKey('studying.Study', on_delete=models.CASCADE)
    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    language = models.CharField(max_length=3, choices=Languages.choices, db_index=True)
    image = models.ImageField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['study', 'language'], name='unique_study'),
        ]
        indexes = [
            models.Index(fields=['study', 'language']),
        ]
        ordering = ['-id']
        permissions = [
            ('access_all_diplomas', _('May access diplomas of all students')),
        ]

        verbose_name = _('Diploma')
        verbose_name_plural = _('Diplomas')
