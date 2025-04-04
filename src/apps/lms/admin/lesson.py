from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from apps.lms.models import Lesson
from apps.notion.id import page_url_to_id, uuid_to_id
from apps.notion.models import Material
from core.admin import ModelAdmin, ModelForm, admin


class LessonForm(ModelForm):
    material = forms.CharField(
        label=_("Material"),
        required=False,
        widget=forms.TextInput(attrs={"placeholder": _("Our slug or notion page_id"), "maxlength": 32}),
    )
    material_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    material_title = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Lesson
        fields = "__all__"

    def get_custom_initial_data(self, lesson: Lesson) -> dict:  # type: ignore
        return {
            "material": uuid_to_id(lesson.material.slug) if lesson.material is not None else None,
        }

    def clean_material(self) -> Material | None:
        """Let user enter id that they can copy from the browser url"""
        material_id = self.cleaned_data["material"]
        if not material_id:
            return None

        if "http" in material_id:
            material_id = page_url_to_id(material_id)

        material = Material.objects.get_by_page_id_or_slug(material_id)
        if material is None:
            raise forms.ValidationError(_("Material not found"))

        return material


@admin.register(Lesson)
class LessonAdmin(ModelAdmin):
    form = LessonForm
    fields = [
        "name",
        "material",
        "question",
        "hidden",
        "material_id",
        "material_title",
    ]
    readonly_fields = ["material_id", "material_title"]
    foreignkey_queryset_overrides = {
        "lms.Lesson.question": lambda apps: apps.get_model("homework.Question").filter(courses__in=apps.get_model("products.Course").for_admin()).distinct(),
    }

    class Media:
        js = ["admin/js/vendor/jquery/jquery.js", "admin/add_material_link.js"]
        css = {
            "all": ["admin/lesson_form.css"],
        }

    def material_id(self, lesson: Lesson) -> int | None:
        return lesson.material_id

    def material_title(self, lesson: Lesson) -> str | None:
        if lesson.material is not None:
            return lesson.material.title

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False


__all__ = [
    "LessonAdmin",
]
