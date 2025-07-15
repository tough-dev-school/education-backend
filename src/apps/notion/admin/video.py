from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from apps.notion.models import Video
from core.admin import ModelAdmin, admin
from core.admin.video import VideoForm
from core.video import get_youtube_video_id


class NotionVideoForm(VideoForm):
    class Meta:
        model = Video
        fields = ("title", "youtube_id", "rutube_id", "rutube_access_key", "youtube", "rutube")

    def clean_youtube(self) -> str:
        youtube_id = get_youtube_video_id(self.cleaned_data.get("youtube") or "")
        if not youtube_id:
            self.add_error("youtube", _("Please add youtube id"))

        videos_with_same_youtube_id = Video.objects.exclude(id=self.instance.id).filter(youtube_id=youtube_id)
        if videos_with_same_youtube_id.exists():
            self.add_error("youtube", _("This video is already in the database"))

        return self.cleaned_data.get("youtube", "")


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
        return f"""<a target="_blank" href="{obj.get_youtube_url()}">
            <img class="notion-youtube-logo" src="/static/logo/youtube.png" />
            {obj.youtube_id}</a>"""

    @admin.display(description=_("RuTube"))
    @mark_safe
    def rutube(self, obj: Video) -> str:
        if obj.rutube_id is not None:
            return f"""<a target="_blank" href="{obj.get_rutube_url()}">
                <img class="notion-rutube-logo" src="/static/logo/rutube.png" />
                {obj.rutube_id}</a>"""

        return "—"
