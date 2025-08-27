from django.apps import apps
from django.db.models import Case, Index, OuterRef, Q, QuerySet, Subquery, Value, When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from core.models import SubqueryCount, TimestampedModel, models


class ModuleQuerySet(QuerySet):
    def for_viewset(self) -> "ModuleQuerySet":
        lessons = apps.get_model("lms.Lesson").objects.filter(module=OuterRef("pk"), hidden=False)

        return (
            self.annotate(lesson_count=SubqueryCount(lessons))
            .annotate(
                single_lesson_id=Case(
                    When(lesson_count=1, then=Subquery(lessons.values("id")[:1])),
                    default=Value(None),
                )
            )
            .order_by("position")
        )

    def exclude_hidden(self) -> "ModuleQuerySet":
        return self.filter(hidden=False)

    def exclude_not_opened(self) -> "ModuleQuerySet":
        return self.filter(
            Q(start_date__isnull=True) | Q(start_date__lte=timezone.now()),
        )

    def for_user(self, user: User) -> "ModuleQuerySet":
        purchased_courses = apps.get_model("studying.Study").objects.filter(student=user).values_list("course_id", flat=True)
        return self.filter(course__in=purchased_courses)

    def for_admin(self) -> "ModuleQuerySet":
        Lesson = apps.get_model("lms.Lesson")
        lessons = Lesson.objects.filter(
            module=OuterRef("pk"),
            hidden=False,
        )
        return self.annotate(
            lesson_count=SubqueryCount(lessons),
        ).select_related("course", "course__group")


class Module(TimestampedModel):
    objects = ModuleQuerySet.as_manager()

    name = models.CharField(max_length=255)
    start_date = models.DateTimeField(_("Start date"), null=True, blank=True)
    description = models.CharField(_("Short description"), blank=True, null=True, max_length=512)
    text = models.TextField(_("Text"), blank=True, null=True)
    course = models.ForeignKey("lms.Course", on_delete=models.CASCADE, related_name="modules")
    hidden = models.BooleanField(_("Hidden"), help_text=_("Users can't find such materials in the listing"), default=True)
    position = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            Index(fields=["course", "position"]),
        ]

        verbose_name = _("Module")
        verbose_name_plural = _("Modules")

    def __str__(self) -> str:
        return f"{self.name} ({self.course})"
