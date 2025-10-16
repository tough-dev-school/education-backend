from typing import Any

from django.contrib.admin.models import CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from core.admin import admin
from core.tasks import write_admin_log


def _get_content_type(queryset: QuerySet) -> str:
    content_type = ContentType.objects.get_for_model(queryset.model)
    return f"{content_type.app_label}.{content_type.model}"


@admin.action(description=_("Put to archive"))
def archive(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    model = _get_content_type(queryset)
    for module in queryset.iterator():
        write_admin_log.delay(
            action_flag=CHANGE,
            model=model,
            change_message=f"{queryset.model._meta.verbose_name.title()} archived (bulk action)",
            object_id=module.id,
            user_id=request.user.id,
        )

    count = queryset.update(archived=True)

    modeladmin.message_user(request, f"{count} {queryset.model._meta.verbose_name_plural} archived")


@admin.action(description=_("Extract from archive"))
def unarchive(modeladmin: Any, request: HttpRequest, queryset: QuerySet) -> None:
    model = _get_content_type(queryset)
    for module in queryset.iterator():
        write_admin_log.delay(
            action_flag=CHANGE,
            model=model,
            change_message=f"{queryset.model._meta.verbose_name.title()} unarchived (bulk action)",
            object_id=module.id,
            user_id=request.user.id,
        )

    count = queryset.update(archived=False)

    modeladmin.message_user(request, f"{count} {queryset.model._meta.verbose_name_plural} unarchived")
