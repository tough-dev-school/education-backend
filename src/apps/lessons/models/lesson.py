from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.db.models import Exists, Index, OuterRef, QuerySet
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.users.models import User
from core.models import SubqueryCount, TimestampedModel, models


class LessonQuerySet(QuerySet):
    def for_viewset(self, user: User | AnonymousUser) -> "LessonQuerySet":
        if user.is_anonymous:
            return self.none()

        return (
            self.for_user(user).with_is_sent(user).with_crosscheck_stats(user).filter(hidden=False).select_related("question", "material").order_by("position")
        )

    def for_user(self, user: User) -> "LessonQuerySet":
        purchased_courses = apps.get_model("studying.Study").objects.filter(student=user).values_list("course_id", flat=True)
        return self.filter(course__in=purchased_courses)

    def with_is_sent(self, user: User) -> "LessonQuerySet":
        Answer = apps.get_model("homework.Answer")
        user_answers = Answer.objects.root_only().filter(
            question=OuterRef("question"),
            author=user,
        )

        return self.annotate(is_sent=Exists(user_answers))

    def with_crosscheck_stats(self, user: User) -> "LessonQuerySet":
        AnswerCrossCheck = apps.get_model("homework.AnswerCrossCheck")

        total = AnswerCrossCheck.objects.filter(
            answer__question=OuterRef("question"),
            checker=user,
        )

        checked = total.filter(checked__isnull=False)

        return self.annotate(
            crosschecks_total=SubqueryCount(total),
            crosschecks_checked=SubqueryCount(checked),
        )


class Lesson(TimestampedModel):
    objects = LessonQuerySet.as_manager()

    name = models.CharField(max_length=255)
    module = models.ForeignKey("lessons.Module", on_delete=models.CASCADE, verbose_name=_("Module"))
    position = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)
    material = models.ForeignKey(
        "notion.Material", blank=True, null=True, related_name="+", on_delete=models.PROTECT, verbose_name=pgettext_lazy("lessons", "Material")
    )
    question = models.ForeignKey(to="homework.Question", blank=True, null=True, related_name="+", on_delete=models.PROTECT, verbose_name=_("Question"))
    hidden = models.BooleanField(_("Hidden"), help_text=_("Users can't find such materials in the listing"), default=True)

    class Meta:
        ordering = ["position"]
        indexes = [
            Index(fields=["module", "position"]),
        ]
