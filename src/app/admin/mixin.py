from typing import Any, Mapping, Optional, Protocol, Type

import re
from collections.abc import Sequence
from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.db.models import Field
from django.template.defaultfilters import capfirst, time
from django.utils import timezone
from django.utils.html import format_html
from prettyjson import PrettyJSONWidget

from app.admin.widgets import AppNumberInput


class DjangoModelAdminProtocol(Protocol):
    @property
    def add_form(self) -> Optional[str]:
        ...

    @property
    def add_fieldsets(self) -> Sequence[tuple[Optional[str], Any]]:
        ...


class AppAdminMixin:
    formfield_overrides: Mapping[Type[Field], Mapping[str, Any]] = {
        models.DecimalField: {'widget': AppNumberInput},
        models.IntegerField: {'widget': AppNumberInput},
        models.JSONField: {'widget': PrettyJSONWidget(attrs={'initial': 'parsed'})},
    }

    exclude: Sequence[str] = [
        'modified',
    ]

    class Media:
        css = {
            'all': ['admin.css', 'prettyjson.css'],
        }

    def get_form(self: DjangoModelAdminProtocol, request: Any, obj: Optional[Type[models.Model]] = None, **kwargs: Any):
        """Use special form during object creation
        """
        defaults = {}
        if obj is None and hasattr(self, 'add_form') and self.add_form is not None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)

        return super().get_form(request, obj, **defaults)  # type: ignore

    def get_fieldsets(self: DjangoModelAdminProtocol, request: Any, obj=None):
        """Use special fieldset during object creation
        """
        if not obj and hasattr(self, 'add_fieldsets') and self.add_fieldsets is not None:
            return self.add_fieldsets

        return super().get_fieldsets(request, obj)  # type: ignore

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
