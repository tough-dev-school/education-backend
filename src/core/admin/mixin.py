import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, Protocol, Type

from django.contrib.humanize.templatetags.humanize import naturalday
from django.db import models
from django.db.models import Field
from django.http import HttpRequest
from django.template.defaultfilters import capfirst, time
from django.utils import timezone
from django.utils.html import format_html
from prettyjson import PrettyJSONWidget

from core.admin.widgets import AppNumberInput


class DjangoModelAdminProtocol(Protocol):
    @property
    def add_form(self) -> str | None: ...

    @property
    def add_fieldsets(self) -> Sequence[tuple[str | None, Any]]: ...


class AppAdminMixin:
    formfield_overrides: Mapping[Type[Field], Mapping[str, Any]] = {
        models.DecimalField: {"widget": AppNumberInput},
        models.IntegerField: {"widget": AppNumberInput},
        models.JSONField: {"widget": PrettyJSONWidget(attrs={"initial": "parsed"})},
    }
    global_exclude = (
        "created",
        "modified",
    )

    class Media:
        css = {
            "all": ["admin.css", "prettyjson.css"],
        }

    def get_exclude(self, request: Any, obj: Any | None = None) -> tuple[str]:
        """Exclude globaly excluded items"""
        return (
            *(super().get_exclude(request, obj) or []),  # type: ignore
            *self.global_exclude,
        )

    def get_form(self: DjangoModelAdminProtocol, request: Any, obj: Type[models.Model] | None = None, **kwargs: Any) -> str | None:
        """Use special form during object creation"""
        defaults = {}
        if obj is None and hasattr(self, "add_form") and self.add_form is not None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)

        return super().get_form(request, obj, **defaults)  # type: ignore

    def get_fieldsets(self: DjangoModelAdminProtocol, request: HttpRequest, obj: Type[models.Model] | None = None) -> Any:
        """Use special fieldset during object creation"""
        if not obj and hasattr(self, "add_fieldsets") and self.add_fieldsets is not None:
            return self.add_fieldsets

        return super().get_fieldsets(request, obj)  # type: ignore

    def _link(self, href: str, text: str) -> str:
        return format_html(f'<a href="{href}">{text}</a>')

    def _email(self, email: str | None) -> str:
        if email is None:
            return "—"

        return self._link("mailto:" + email, email)

    def _natural_datetime(self, date: datetime) -> str:
        local = timezone.localtime(date)
        return capfirst(naturalday(local)) + " " + self._time(local)  # type: ignore

    def _time(self, date: datetime) -> str:
        return time(date, "TIME_FORMAT")

    def _phone(self, phone: str | None) -> str:
        if phone is None:
            return "—"
        return self._link(
            href="tel:" + re.sub(r"[^\d\+]+", "", phone),
            text=phone,
        )
