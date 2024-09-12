from typing import Any, Mapping, no_type_check

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.notion import helpers
from apps.notion.models import Video
from core.admin import ModelAdmin, admin


class NotionVideoForm(forms.ModelForm):
    title = forms.CharField(label=_("Title"), widget=forms.Textarea(), required=False)
    youtube = forms.CharField(label=_("Youtube"), required=True, help_text=_("Paste it from the address bar"))
    rutube = forms.CharField(label=_("RuTube"), required=False, help_text=_("Paste it from the address bar"))

    youtube_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    rutube_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    rutube_access_key = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Video
        fields = ("title", "youtube_id", "rutube_id", "rutube_access_key", "youtube", "rutube")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if self.instance.id is not None:
            self.fields["youtube"].initial = self.instance.get_youtube_url()
            self.fields["rutube"].initial = self.instance.get_rutube_url() if self.instance.rutube_id else None

    @no_type_check
    def get_youtube_id(self) -> str:
        youtube_id = helpers.get_youtube_video_id(self.cleaned_data.get("youtube")) or ""

        if youtube_id:
            videos_with_same_youtube_id = Video.objects.exclude(id=self.instance.id).filter(youtube_id=youtube_id)
            if videos_with_same_youtube_id.exists():
                self.add_error("youtube", _("This video is already in the database"))

        return youtube_id

    @no_type_check
    def clean(self) -> Mapping[str, str]:
        cleaned_data = super().clean()

        cleaned_data["youtube_id"] = self.get_youtube_id()
        cleaned_data["rutube_id"] = helpers.get_rutube_video_id(cleaned_data.get("rutube") or "")
        cleaned_data["rutube_access_key"] = helpers.get_rutube_access_key(cleaned_data.get("rutube") or "")

        return cleaned_data


@admin.register(Video)
class NotionVideoAdmin(ModelAdmin):
    form = NotionVideoForm

    list_display = [
        "id",
        "title",
        "youtube",
        "rutube",
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
