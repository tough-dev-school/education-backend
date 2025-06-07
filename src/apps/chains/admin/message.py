from django.contrib.admin import RelatedOnlyFieldListFilter
from django.db.models import F, QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.chains.admin.forms import MessageAddForm, MessageEditForm
from apps.chains.models import Message
from apps.products.admin.filters import CourseFilter
from core.admin import ModelAdmin, admin


@admin.register(Message)
class MessageAdmin(ModelAdmin):
    add_form = MessageAddForm
    form = MessageEditForm

    def get_queryset(self, request: HttpRequest) -> QuerySet[Message]:
        qs = super().get_queryset(request).not_archived()  # type: ignore
        return qs.annotate(course_id=F("chain__course_id"))

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
        CourseFilter,
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
