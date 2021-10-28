import re
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.template.defaultfilters import capfirst, time
from django.utils import timezone
from django.utils.html import format_html

from app.admin.widgets import AppNumberInput


class AppAdminMixin:
    formfield_overrides = {
        models.DecimalField: {'widget': AppNumberInput},
        models.IntegerField: {'widget': AppNumberInput},
    }
    exclude = [
        'modified',
    ]

    class Media:
        css = {
            'all': ['admin.css'],
        }

    def get_form(self, request, obj=None, **kwargs):
        """Use special form during object creation
        """
        defaults = {}
        if obj is None and hasattr(self, 'add_form') and self.add_form is not None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)

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
