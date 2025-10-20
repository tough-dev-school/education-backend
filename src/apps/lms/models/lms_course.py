from django.apps import apps
from django.db.models import OuterRef, QuerySet
from django.utils.translation import pgettext_lazy

from apps.products.models import Course as _Course
from core.models import SubqueryCount, models


class CourseQuerySet(QuerySet):
    def for_admin(self) -> "CourseQuerySet":
        Module = apps.get_model("lms.Module")
        modules = Module.objects.filter(
            course=OuterRef("pk"),
            hidden=False,
        )
        return self.annotate(
            module_count=SubqueryCount(modules),
        )


class CourseManager(models.Manager.from_queryset(CourseQuerySet)):
    def get_queryset(self) -> CourseQuerySet:
        return super().get_queryset().select_related("group")


class Course(_Course):
    """Proxy model for admin matters"""

    objects = CourseManager()

    class Meta:
        proxy = True
        ordering = ["-created"]
        verbose_name = pgettext_lazy("lms", "Course")
        verbose_name_plural = pgettext_lazy("lms", "Courses")


__all__ = [
    "Course",
]
