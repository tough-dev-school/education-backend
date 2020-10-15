from urllib.parse import urljoin

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from app.models import models
from courses.models.base import Shippable


class Course(Shippable):
    name_genitive = models.CharField(_('Genitive name'), max_length=255, help_text='«мастер-класса о TDD». К примеру для записей.')
    clickmeeting_room_url = models.URLField(_('Clickmeeting room URL'), null=True, blank=True, help_text=_('If set, every user who purcashes this course gets invited'))
    zoomus_webinar_id = models.CharField(_('Zoom.us webinar ID'), max_length=255, null=True, blank=True, help_text=_('If set, every user who purcashes this course gets invited'))

    welcome_letter_template_id = models.CharField(_('Welcome letter template id'), max_length=255, blank=True, null=True, help_text=_('Will be sent upon purchase if set'))

    class Meta:
        ordering = ['-id']
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, '/'.join(['courses', self.slug, '']))
