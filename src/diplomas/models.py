import shortuuid
from django.utils.translation import gettext_lazy as _

from app.files import RandomFileName
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
    slug = models.CharField(max_length=32, db_index=True, unique=True, default=shortuuid.uuid)
    language = models.CharField(max_length=3, choices=Languages.choices, db_index=True)
    image = models.ImageField(upload_to=RandomFileName('diplomas'))

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

    def get_other_languages(self) -> DiplomaQuerySet:
        return self.__class__.objects.filter(study=self.study).exclude(pk=self.pk)
