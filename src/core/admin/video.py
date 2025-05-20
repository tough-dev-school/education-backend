from typing import Any

from django import forms
from django.utils.translation import gettext_lazy as _

from core.admin import ModelForm
from core.video import get_rutube_access_key, get_rutube_video_id, get_youtube_video_id


class VideoForm(ModelForm):
    youtube = forms.CharField(label=_("Youtube"), required=True, help_text=_("Paste it from the address bar"))
    rutube = forms.CharField(label=_("RuTube"), required=False, help_text=_("Paste it from the address bar"))

    youtube_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    rutube_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    rutube_access_key = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if self.instance.id is not None:
            self.fields["youtube"].initial = self.instance.get_youtube_url()
            self.fields["rutube"].initial = self.instance.get_rutube_url() if self.instance.rutube_id else None

    def get_youtube_id(self) -> str | None:
        youtube_id = get_youtube_video_id(self.cleaned_data.get("youtube") or "")

        if youtube_id:
            videos_with_same_youtube_id = self.__class__.Meta.model.objects.exclude(id=self.instance.id).filter(youtube_id=youtube_id)  # type: ignore
            if videos_with_same_youtube_id.exists():
                self.add_error("youtube", _("This video is already in the database"))

        return youtube_id

    def clean(self) -> dict[str, Any] | None:
        cleaned_data = super().clean()

        if cleaned_data is None:
            return None

        cleaned_data["youtube_id"] = self.get_youtube_id()
        cleaned_data["rutube_id"] = get_rutube_video_id(cleaned_data.get("rutube") or "")
        cleaned_data["rutube_access_key"] = get_rutube_access_key(cleaned_data.get("rutube") or "")

        del cleaned_data['youtube']
        del cleaned_data['rutube']

        return cleaned_data


__all__ = [
    "VideoForm",
]
