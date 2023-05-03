from django.contrib.admin import RelatedOnlyFieldListFilter
from django.db.models import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from app.admin import admin
from app.admin import ModelAdmin
from chains.admin.forms import MessageAddForm
from chains.admin.forms import MessageEditForm
from chains.models import Message


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    add_form = MessageAddForm
    form = MessageEditForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Message]:
        return super().get_queryset(request).not_archived()  # type: ignore

    fields = [
        "name",
        "chain",
        "parent",
        "template_id",
        "delay",
    ]

    list_display = [
        "id",
        "name",
        "course",
        "chain",
        "parent",
        "template_id",
        "delay",
    ]

    list_filter = [
        ("chain__course", RelatedOnlyFieldListFilter),
        ("chain", RelatedOnlyFieldListFilter),
    ]

    list_select_related = [
        "parent",
        "chain",
        "chain__course",
    ]

    @admin.display(description=_("Course"), ordering="chain__course")
    def course(self, obj: Message) -> str:
        return str(obj.chain.course)


__all__ = [
    "MessageAdmin",
]
