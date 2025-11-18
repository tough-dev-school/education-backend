from typing import Any

from django.db import transaction
from django.db.models import QuerySet, Value
from django.db.models.functions import Replace
from django.http.request import HttpRequest
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from httpx import HTTPError

from apps.notion import tasks
from apps.notion.client import NotionClient
from apps.notion.exceptions import NotionError
from apps.notion.id import page_url_to_id, uuid_to_id
from apps.notion.models import Material, NotionCacheEntryStatus
from apps.products.admin.filters import CourseFilter
from core.admin import ModelAdmin, ModelForm, admin


class NotionMaterialForm(ModelForm):
    class Meta:
        model = Material
        fields = "__all__"

    def clean_page_id(self) -> str:
        return page_url_to_id(self.cleaned_data["page_id"])

    def clean_title(self) -> str:
        """Fetch page title from apps.notion"""
        if len(self.cleaned_data["title"]) == 0 and "https://" in self.data["page_id"]:
            notion = NotionClient()
            try:
                page = notion.fetch_page_root(page_url_to_id(self.data["page_id"]))
            except (HTTPError, NotionError):
                return ""

            if page.title is not None:
                return page.title

        return self.cleaned_data["title"]


@admin.action(description=_("Update"))
def update(modeladmin: Any, request: HttpRequest, queryset: QuerySet[Material]) -> None:
    material_count = 0
    for material in queryset.iterator():  # manualy update cache status before running the task, so user will get 'updating...' near each requested material
        with transaction.atomic():
            NotionCacheEntryStatus.objects.filter(
                page_id=material.page_id,
            ).update(
                fetch_complete=None,
                fetch_started=timezone.now(),
            )

        tasks.update_cache.delay(page_id=material.page_id)
        material_count += 1

    modeladmin.message_user(
        request,
        _(f"Started updating {material_count} materials"),
    )


@admin.register(Material)
class NotionMaterialAdmin(ModelAdmin):
    list_display = (
        "title",
        "status",
        "our_page",
        "notion_page",
    )
    fields = [
        "title",
        "course",
        "page_id",
        "is_home_page",
    ]
    search_fields = [
        "slug",
        "page_id",
    ]
    lookup_fields = [
        "page_id",
        "slug_without_dashes",
    ]
    actions = [
        update,
    ]

    list_filter = (CourseFilter,)
    form = NotionMaterialForm
    save_as = True

    class Media:
        css = {"all": ("admin/css/material_admin.css",)}

    def get_queryset(self, request: HttpRequest) -> QuerySet[Material]:
        return Material.objects.with_cache_status()

    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> tuple[QuerySet, bool]:
        """Allow searching both by long and short ids"""
        if len(search_term) == 36:
            search_term = uuid_to_id(search_term)

        queryset.annotate(slug_without_dashes=Replace("slug", Value("-"), Value("")))
        return super().get_search_results(request, queryset, search_term)

    @admin.display(description=_("LMS"))
    @mark_safe
    def our_page(self, material: Material) -> str:
        lms_url = material.get_absolute_url()

        return f"""<a target="_blank" href="{lms_url}">
            <img class="notion-lms-logo" src="/static/logo/tds.png" />
            Открыть</a>"""

    @admin.display(description=_("Notion"))
    @mark_safe
    def notion_page(self, material: Material) -> str:
        notion_url = material.get_notion_url()
        return f"""<a target="_blank" href="{notion_url}">
            <img class="notion-logo" src="/static/logo/notion.svg" />
            Открыть</a>"""

    @admin.display(description=_("Status"), ordering="-fetch_complete")
    def status(self, material: Material) -> str:
        if not material.fetch_started and not material.fetch_complete:
            return "—"

        if not material.fetch_complete:
            return "Обновляется..."

        return self._natural_datetime(material.fetch_complete)
