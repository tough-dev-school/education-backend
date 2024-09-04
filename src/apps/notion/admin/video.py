from typing import no_type_check

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.notion import helpers
from apps.notion.models import Video
from core.admin import ModelAdmin, admin


class NotionVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = "__all__"

    @no_type_check
    def clean_rutube_id(self) -> str:
        return helpers.get_rutube_video_id(self.cleaned_data["rutube_id"])

    @no_type_check
    def clean_youtube_id(self) -> str:
        return helpers.get_youtube_video_id(self.cleaned_data["youtube_id"])


@admin.register(Video)
class NotionVideoAdmin(ModelAdmin):
    form = NotionVideoForm

    list_display = [
        "id",
        "youtube",
        "rutube",
    ]
    fields = [
        "youtube_id",
        "rutube_id",
    ]

    @admin.display(description=_("Youtube"))
    @mark_safe
    def youtube(self, obj: Video) -> str:
        return f"""<a target="_blank" href="{ obj.get_youtube_url() }">
            <img class="notion-youtube-logo" src="/static/logo/youtube.png" />
            {obj.youtube_id}</a>"""

    @admin.display(description=_("RuTube"))
    @mark_safe
    def rutube(self, obj: Video) -> str:
        if obj.rutube_id is not None:
            return f"""<a target="_blank" href="{ obj.get_rutube_url() }">
                <img class="notion-rutube-logo" src="/static/logo/rutube.png" />
                {obj.rutube_id}</a>"""

        return "—"
