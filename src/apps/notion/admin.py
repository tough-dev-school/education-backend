from django import forms
from django.db.models import QuerySet, Value
from django.db.models.functions import Replace
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _
from httpx import HTTPError

from apps.notion import helpers
from apps.notion.client import NotionClient
from apps.notion.exceptions import NotionError
from apps.notion.models import Material, MaterialFile
from core.admin import ModelAdmin, admin


class NotionMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = "__all__"

    def clean_page_id(self) -> str:
        return helpers.page_url_to_id(self.cleaned_data["page_id"])

    def clean_title(self) -> str:
        """Fetch page title from apps.notion"""
        if len(self.cleaned_data["title"]) == 0 and "https://" in self.data["page_id"]:
            notion = NotionClient()
            try:
                page = notion.fetch_page(helpers.page_url_to_id(self.data["page_id"]))
            except (HTTPError, NotionError):
                return ""

            if page.title is not None:
                return page.title

        return self.cleaned_data["title"]


@admin.register(Material)
class NotionMaterialAdmin(ModelAdmin):
    list_display = (
        "title",
        "our_page_id",
        "page_id",
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

    list_display_links = list_display
    list_filter = ("course",)
    form = NotionMaterialForm
    save_as = True

    def get_search_results(self, request: HttpRequest, queryset: QuerySet, search_term: str) -> tuple[QuerySet, bool]:
        """Allow searching both by long and short ids"""
        if len(search_term) == 36:
            search_term = helpers.uuid_to_id(search_term)

        queryset.annotate(slug_without_dashes=Replace("slug", Value("-"), Value("")))
        return super().get_search_results(request, queryset, search_term)

    @admin.display(description=_("Our page id"))
    def our_page_id(self, obj: Material) -> str:
        return helpers.uuid_to_id(str(obj.slug))


@admin.register(MaterialFile)
class MaterialFileAdmin(ModelAdmin): ...
