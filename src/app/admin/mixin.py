import re

from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.template.defaultfilters import capfirst, time
from django.utils import timezone
from django.utils.html import format_html

from app.admin.widgets import Select2Widget


class AppAdminMixin:
    formfield_overrides = {
        models.ForeignKey: {'widget': Select2Widget},
    }
    exclude = [
        'modified',
    ]

    def _link(self, href, text):
        return format_html(f'<a href="{href}">{text}</a>')

    def _email(self, email):
        if email is None:
            return '—'

        return self._link('mailto:' + email, email)

    def _natural_datetime(self, date):
        local = timezone.localtime(date)
        return capfirst(naturalday(local)) + ' ' + self._time(local)

    def _time(self, date):
        return time(date, 'TIME_FORMAT')

    def _phone(self, phone):
        if phone is None:
            return '—'
        return self._link(
            href='tel:' + re.sub(r'[^\d\+]+', '', phone),
            text=phone,
        )
