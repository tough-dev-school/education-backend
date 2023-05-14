from httpx import HTTPError

from django import forms

from app.admin import admin
from app.admin import ModelAdmin
from notion import helpers
from notion.client import NotionClient
from notion.exceptions import NotionError
from notion.models import Material
from notion.models import MaterialFile


class NotionMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = "__all__"

    def clean_page_id(self) -> str:
        return helpers.page_url_to_id(self.cleaned_data["page_id"])

    def clean_title(self) -> str:
        """Fetch page title from notion"""
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
        "course",
        "page_id",
    )
    fields = [
        "title",
        "course",
        "page_id",
        "is_home_page",
    ]
    list_display_links = list_display
    list_filter = ("course",)
    form = NotionMaterialForm
    save_as = True


@admin.register(MaterialFile)
class MaterialFileAdmin(ModelAdmin):
    ...
