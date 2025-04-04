from django.apps import apps
from django.db.models import OuterRef, QuerySet
from django.utils.translation import pgettext_lazy

from apps.products.models import Course as _Course
from core.models import SubqueryCount


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


class Course(_Course):
    """Proxy model for admin matters"""

    objects = CourseQuerySet.as_manager()  # type: ignore

    class Meta:
        proxy = True
        ordering = ["-created"]
        verbose_name = pgettext_lazy(message="Course", context="lms")
        verbose_name_plural = pgettext_lazy(message="Courses", context="lms")


__all__ = [
    "Course",
]
