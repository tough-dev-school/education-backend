from apps.lms.models import Call
from core.admin import ModelAdmin, admin
from core.admin.video import VideoForm


class CallForm(VideoForm):
    class Meta:
        model = Call
        fields = (
            "name",
            "url",
            "youtube_id",
            "rutube_id",
            "rutube_access_key",
            "youtube",
            "rutube",
        )


@admin.register(Call)
class CallAdmin(ModelAdmin):
    form = CallForm


__all__ = ["CallAdmin"]
