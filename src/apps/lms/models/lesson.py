from django.apps import apps
from django.db.models import Exists, Index, IntegerField, OuterRef, QuerySet, Value
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from apps.users.models import User
from core.models import SubqueryCount, TimestampedModel, models


class LessonQuerySet(QuerySet):
    def for_viewset(self) -> "LessonQuerySet":
        return (
            self.filter(
                hidden=False,
            )
            .select_related(
                "question",
                "material",
            )
            .order_by("position")
        )

    def with_annotations(self, user: User) -> "LessonQuerySet":
        return self.with_comment_count(user).with_is_sent(user).with_crosscheck_stats(user)

    def with_fake_annotations(self) -> "LessonQuerySet":
        return self.annotate(
            is_sent=Value(False),
            crosschecks_total=Value(0),
            crosschecks_checked=Value(0),
            comment_count=Value(0),
        )

    def for_user(self, user: User) -> "LessonQuerySet":
        purchased_courses = apps.get_model("studying.Study").objects.filter(student=user).values_list("course_id", flat=True)
        return self.filter(
            module__course__in=purchased_courses,
        )

    def for_admin(self) -> "LessonQuerySet":
        return self.select_related(
            "module",
            "module__course",
            "module__course__group",
            "material",
            "call",
        )

    def with_comment_count(self, user: User) -> "LessonQuerySet":
        return self.annotate(
            comment_count=RawSQL(  # django-treeqeury is 3 times slower here
                """
                SELECT COUNT(child.id)
                FROM homework_answer AS child
                JOIN homework_answer AS parent ON child.parent_id = parent.id
                WHERE parent.question_id = lms_lesson.question_id
                AND parent.parent_id IS NULL
                AND parent.author_id = %s
                AND child.author_id != %s
                """,
                [user.id, user.id],
                output_field=IntegerField(),
            ),
        )

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

    module = models.ForeignKey("lms.Module", on_delete=models.CASCADE, verbose_name=_("Module"))
    position = models.PositiveIntegerField(default=0, blank=False, null=False, db_index=True)
    material = models.ForeignKey(
        "notion.Material", blank=True, null=True, related_name="+", on_delete=models.PROTECT, verbose_name=pgettext_lazy("lessons", "Material")
    )
    question = models.ForeignKey(
        to="homework.Question", blank=True, null=True, related_name="+", on_delete=models.PROTECT, verbose_name=pgettext_lazy("lms", "Question")
    )

    call = models.ForeignKey("lms.Call", blank=True, null=True, on_delete=models.CASCADE, verbose_name=pgettext_lazy("lms", "Call"))
    hidden = models.BooleanField(_("Hidden"), help_text=_("Users can't find such materials in the listing"), default=False)

    class Meta:
        ordering = ["position"]
        indexes = [
            Index(fields=["module", "position"]),
        ]
        verbose_name = pgettext_lazy("lms", "Lesson")
        verbose_name_plural = pgettext_lazy("lms", "Lessons")

    def __str__(self) -> str:
        if self.material_id is not None:
            return str(self.material)

        if self.question_id is not None:
            return str(self.question)

        if self.call_id is not None:
            return str(self.call)

        return "—"

    def get_allowed_comment_count(self, user: User) -> int:
        count = 0
        for answer in apps.get_model("homework.Answer").objects.filter(question=self.question_id, author=user).root_only():
            count += answer.get_limited_comments_for_user_by_crosschecks(user).count()

        return count
