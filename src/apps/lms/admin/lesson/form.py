from django import forms
from django.utils.translation import gettext_lazy as _

from apps.lms.models import Lesson
from apps.notion.id import page_url_to_id, uuid_to_id
from apps.notion.models import Material
from core.admin.forms import ModelForm


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
