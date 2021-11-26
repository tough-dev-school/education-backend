import shortuuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from urllib.parse import urljoin

from app.files import RandomFileName
from app.models import DefaultQuerySet, TimestampedModel, models
from app.tasks import send_mail
from users.models import User


class Languages(models.TextChoices):
    RU = 'RU', _('Russian')
    EN = 'EN', _('English')


class DiplomaQuerySet(DefaultQuerySet):
    def for_viewset(self):
        return self.select_related('study', 'study__student', 'study__course')

    def for_user(self, user):
        return self.filter(study__student=user)


class Diploma(TimestampedModel):

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

    def get_absolute_url(self) -> str:
        return urljoin(settings.DIPLOMA_FRONTEND_URL, f'/{self.slug}/')

    def send_to_student(self):
        send_mail.delay(
            to=self.study.student.email,
            template_id='new-diploma',
            ctx=dict(
                course_name=self.study.course.full_name,
                diploma_url=self.get_absolute_url(),
            ),
            disable_antispam=True,
        )

    def regenerate(self) -> int:
        """Regenerate diploma for self and all other diplomas that match given course"""
        count = 0
        for template in DiplomaTemplate.objects.filter(course=self.study.course):
            template.generate_diploma(student=self.study.student)
            count += 1

        return count


class DiplomaTemplate(TimestampedModel):
    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)
    slug = models.CharField(max_length=32, help_text=_('Check out https://is.gd/eutOYr for available templates'))
    language = models.CharField(max_length=3, choices=Languages.choices, db_index=True)
    homework_accepted = models.BooleanField(_('This template is for students that have completed the homework'), default=False)

    class Meta:
        verbose_name = _('Diploma template')
        verbose_name_plural = _('Diploma templates')

        constraints = [
            models.UniqueConstraint(fields=['course', 'language', 'homework_accepted'], name='single diploma per course option'),
        ]

        indexes = [
            models.Index(fields=['course', 'language', 'homework_accepted']),
        ]

    def generate_diploma(self, student: User):
        from diplomas.tasks import generate_diploma

        generate_diploma.delay(
            student_id=student.pk,
            course_id=self.course.pk,
            language=self.language,
        )
