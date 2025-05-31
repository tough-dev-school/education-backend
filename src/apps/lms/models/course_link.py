from django.utils.translation import gettext_lazy as _

from core.models import TimestampedModel, models


class CourseLink(TimestampedModel):
    course = models.ForeignKey("lms.Course", on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=255)
    url = models.CharField(_("URL"), max_length=255)

    class Meta:
        verbose_name = _("Course link")
        verbose_name_plural = _("Course links")
