from typing import Any

from django.contrib.admin.models import CHANGE
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.lms.models import Module
from core.admin import admin
from core.tasks import write_admin_log


@admin.action(description=_("Put to archive"))
def archive(modeladmin: Any, request: HttpRequest, queryset: QuerySet[Module]) -> None:
    for module in queryset.iterator():
        write_admin_log.delay(
            action_flag=CHANGE,
            app="lms",
            model="Module",
            change_message="Module archived (bulk action)",
            object_id=module.id,
            user_id=request.user.id,
        )

    count = queryset.update(archived=True)

    modeladmin.message_user(request, f"{count} modules archived")


@admin.action(description=_("Extract from archive"))
def unarchive(modeladmin: Any, request: HttpRequest, queryset: QuerySet[Module]) -> None:
    for module in queryset.iterator():
        write_admin_log.delay(
            action_flag=CHANGE,
            app="lms",
            model="Module",
            change_message="Module unarchived (bulk action)",
            object_id=module.id,
            user_id=request.user.id,
        )

    count = queryset.update(archived=False)

    modeladmin.message_user(request, f"{count} modules unarchived")
