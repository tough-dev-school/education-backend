import uuid
from typing import TYPE_CHECKING, Optional
from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.db.models import Exists, OuterRef, QuerySet, Value
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from core.models import SubqueryCount, TimestampedModel, models

if TYPE_CHECKING:
    from apps.products.models import Course


class QuestionQuerySet(QuerySet):
    def for_admin(self) -> "QuestionQuerySet":
        return self

    def for_user(self, user: User) -> "QuestionQuerySet":
        if user.has_perm("studying.purchased_all_courses") or user.has_perm("homework.see_all_questions"):
            return self.with_fake_annotations()

        return self.with_annotations(
            user,
        ).limit_to_questions_from_purchased_course(
            user,
        )

    def limit_to_questions_from_purchased_course(self, user: User) -> "QuestionQuerySet":
        purchased_lessons = apps.get_model("lms.Lesson").objects.for_user(user).exclude(question=None)

        return self.filter(pk__in=purchased_lessons.values("question").distinct())

    def with_annotations(self, user: User) -> "QuestionQuerySet":
        return self.with_is_sent(user).with_comment_count(user).with_crosscheck_stats(user)

    def with_fake_annotations(self) -> "QuestionQuerySet":
        return self.annotate(
            is_sent=Value(False),
            crosschecks_total=Value(0),
            crosschecks_checked=Value(0),
            comment_count=Value(0),
        )

    def with_is_sent(self, user: User) -> "QuestionQuerySet":
        Answer = apps.get_model("homework.Answer")
        user_answers = Answer.objects.root_only().filter(
            question=OuterRef("pk"),
            author=user,
        )

        return self.annotate(is_sent=Exists(user_answers))

    def with_comment_count(self, user: User) -> "QuestionQuerySet":
        return self.annotate(
            comment_count=RawSQL(  # django-treeqeury is 3 times slower here
                """
                SELECT COUNT(child.id)
                FROM homework_answer AS child
                JOIN homework_answer AS parent ON child.parent_id = parent.id
                WHERE parent.question_id = homework_question.id
                AND parent.parent_id IS NULL
                AND parent.author_id = %s
                AND child.author_id != %s
                """,
                [user.id, user.id],
                output_field=models.IntegerField(),
            ),
        )

    def with_crosscheck_stats(self, user: User) -> "QuestionQuerySet":
        AnswerCrossCheck = apps.get_model("homework.AnswerCrossCheck")

        total = AnswerCrossCheck.objects.filter(
            answer__question=OuterRef("pk"),
            checker=user,
        )

        checked = total.filter(checked__isnull=False)

        return self.annotate(
            crosschecks_total=SubqueryCount(total),
            crosschecks_checked=SubqueryCount(checked),
        )


class Question(TimestampedModel):
    objects = QuestionQuerySet.as_manager()

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    name = models.CharField(_("Name"), max_length=256)

    text = models.TextField()

    deadline = models.DateTimeField(_("Deadline"), null=True, blank=True)

    _legacy_course = models.ForeignKey("products.Course", null=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("Homework")
        verbose_name_plural = _("Homeworks")
        permissions = [
            ("see_all_questions", _("May see questions for all homeworks")),
        ]

    def get_absolute_url(self) -> str:
        return urljoin(settings.FRONTEND_URL, f"homework/question-admin/{self.slug}/")

    def dispatch_crosscheck(self, **kwargs: dict) -> int:
        from apps.homework.services import QuestionCrossCheckDispatcher

        dispatcher = QuestionCrossCheckDispatcher(question=self, **kwargs)  # type: ignore

        return dispatcher()

    def get_allowed_comment_count(self, user: User) -> int:
        count = 0
        for answer in apps.get_model("homework.Answer").objects.filter(question=self, author=user).root_only():
            count += answer.get_limited_comments_for_user_by_crosschecks(user).count()

        return count

    def get_legacy_course(self) -> Optional["Course"]:
        return self._legacy_course

    def get_course(self, user: User) -> Optional["Course"]:
        purchased_lessons = (
            apps.get_model("lms.Lesson")
            .objects.for_user(
                user,
            )
            .filter(
                question=self,
            )
            .values("module")
            .distinct()
        )
        purchased_modules = apps.get_model("lms.Module").objects.filter(
            pk__in=purchased_lessons,
        )

        return (
            apps.get_model("products.Course")
            .objects.filter(
                pk__in=purchased_modules.values("course"),
            )
            .first()
        )
