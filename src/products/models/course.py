from django.apps import apps
from django.db.models import OuterRef, QuerySet, Subquery
from django.utils.translation import gettext_lazy as _

from app.models import models
from app.tasks import send_mail
from products.models.base import Shippable
from users.models import User


class CourseQuerySet(QuerySet):
    def for_lms(self) -> QuerySet['Course']:
        return self.filter(
            display_in_lms=True,
        ).with_course_homepage()

    def with_course_homepage(self) -> QuerySet['Course']:
        materials = apps.get_model('notion.Material').objects.filter(
            course=OuterRef('pk'),
            is_home_page=True,
        ).order_by(
            '-created',
        ).values(
            'page_id',
        )

        return self.annotate(
            home_page_slug=Subquery(materials[:1]),
        )


class Course(Shippable):
    objects = models.Manager.from_queryset(CourseQuerySet)()

    name_genitive = models.CharField(_('Genitive name'), max_length=255, help_text='«мастер-класса о TDD». К примеру для записей.')
    zoomus_webinar_id = models.CharField(_('Zoom.us webinar ID'), max_length=255, null=True, blank=True, help_text=_('If set, every user who purcashes this course gets invited'))

    welcome_letter_template_id = models.CharField(_('Welcome letter template id'), max_length=255, blank=True, null=True, help_text=_('Will be sent upon purchase if set'))
    gift_welcome_letter_template_id = models.CharField(_('Special welcome letter template id for gifts'), max_length=255, blank=True, null=True, help_text=_('If not set, common welcome letter will be used'))
    display_in_lms = models.BooleanField(_('Display in LMS'), default=True, help_text=_('If disabled will not be shown in LMS'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
        db_table = 'courses_course'

    def get_purchased_users(self) -> QuerySet[User]:
        return User.objects.filter(
            pk__in=apps.get_model('studying.Study').objects.filter(course=self).values_list('student', flat=True),
        )

    def send_email_to_all_purchased_users(self, template_id: str):
        for user in self.get_purchased_users().iterator():
            send_mail.delay(
                to=user.email,
                template_id=template_id,
            )
