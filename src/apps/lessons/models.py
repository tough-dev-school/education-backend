from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.db.models import Index, QuerySet
from django.utils.translation import gettext_lazy as _

from apps.products.models import Course as _Course
from apps.users.models import User
from core.models import TimestampedModel, models


class Course(_Course):
    class Meta:
        proxy = True
        ordering = ["-created"]


class LessonQuerySet(QuerySet):
    def for_viewset(self) -> "LessonQuerySet":
        return self.filter(hidden=False).order_by("position")

    def for_user(self, user: User | AnonymousUser) -> "LessonQuerySet":
        if user.is_anonymous:
            return self.none()

        purchased_courses = apps.get_model("studying.Study").objects.filter(student=user).values_list("course_id", flat=True)
        return self.filter(course__in=purchased_courses)


class Lesson(TimestampedModel):
    objects = LessonQuerySet.as_manager()

    name = models.CharField(max_length=255)
    course = models.ForeignKey("products.Course", on_delete=models.CASCADE, related_name="lessons")
    position = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)
    material = models.ForeignKey("notion.Material", blank=True, null=True, related_name="+", on_delete=models.PROTECT)
    question = models.ForeignKey("homework.Question", blank=True, null=True, related_name="+", on_delete=models.PROTECT)
    hidden = models.BooleanField(_("Hidden"), help_text=_("Users can't find such materials in the listing"), default=True)


    class Meta:
        ordering = ["position"]
        indexes = [
            Index(fields=["course", "position"]),
        ]
