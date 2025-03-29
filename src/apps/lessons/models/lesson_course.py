from django.apps import apps
from django.db.models import OuterRef, QuerySet
from django.utils.translation import pgettext_lazy

from apps.products.models import Course
from core.models import SubqueryCount


class LessonCourseQuerySet(QuerySet):
    def for_admin(self) -> "LessonCourseQuerySet":
        Lesson = apps.get_model("lessons.Lesson")
        course_lessons = Lesson.objects.filter(
            course=OuterRef("pk"),
            hidden=False,
        )
        return self.annotate(
            lesson_count=SubqueryCount(course_lessons),
        )


class LessonCourse(Course):
    """Proxy model for admin matters"""

    objects = LessonCourseQuerySet.as_manager()  # type: ignore

    class Meta:
        proxy = True
        ordering = ["-created"]
        verbose_name = pgettext_lazy(message="Course", context="lessons")
        verbose_name_plural = pgettext_lazy(message="Courses", context="lessons")
