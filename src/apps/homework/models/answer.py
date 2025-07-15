import textwrap
import uuid
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.db.models import Count, IntegerField, Prefetch
from django.db.models.expressions import RawSQL
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from tree_queries.models import TreeNode
from tree_queries.query import TreeQuerySet

from apps.homework.models.reaction import Reaction
from apps.users.models import User
from core.markdown import markdownify, remove_html
from core.models import TestUtilsMixin, models


class AnswerQuerySet(TreeQuerySet):
    def for_viewset(self) -> "AnswerQuerySet":
        return self.with_tree_fields().with_children_count().select_related("author", "question")

    def prefetch_reactions(self) -> "AnswerQuerySet":
        """
        Prefetch reactions for the queryset
        """
        return self.prefetch_related(Prefetch("reactions", queryset=Reaction.objects.for_viewset()))

    def with_crosscheck_count(self) -> "AnswerQuerySet":
        return self.annotate(crosscheck_count=Count("answercrosscheck"))

    def for_user(self, user: User) -> "AnswerQuerySet":
        return self.filter(author=user)

    def root_only(self) -> "AnswerQuerySet":
        return self.filter(parent__isnull=True)

    def with_children_count(self) -> "AnswerQuerySet":
        return self.annotate(  # SQL here cuz django-tree-queries make too long queries
            children_count=RawSQL(
                """
                SELECT COUNT(*)
                FROM homework_answer AS child
                WHERE child.parent_id = homework_answer.id
                """,
                [],
                output_field=IntegerField(),
            )
        )


class Answer(TestUtilsMixin, TreeNode):
    objects = AnswerQuerySet.as_manager()

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    question = models.ForeignKey("homework.Question", on_delete=models.PROTECT, related_name="+")
    study = models.ForeignKey("studying.Study", null=True, on_delete=models.SET_NULL, related_name="+")
    author = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="+")
    do_not_crosscheck = models.BooleanField(_("Exclude from cross-checking"), default=False, db_index=True)

    text = models.TextField()

    class Meta:
        verbose_name = _("Homework answer")
        verbose_name_plural = _("Homework answers")
        ordering = ["created"]
        permissions = [
            ("see_all_answers", _("May see answers from every user")),
        ]
        indexes = [
            models.Index(fields=["question", "author"]),
            models.Index(fields=["question", "study"]),
        ]

    def __str__(self) -> str:
        if self.text.startswith("![]"):
            return "Картинка"

        text = remove_html(markdownify(self.text))
        try:
            first_word = text.split()[0]
        except IndexError:  # zero length
            first_word = ""
        resource = urlparse(first_word).netloc
        if resource:
            return f"Ссылка на {resource}"

        return textwrap.shorten(text, width=40)

    def get_absolute_url(self) -> str:
        root = self.get_root_answer()

        url = urljoin(settings.FRONTEND_URL, f"homework/answers/{root.slug}/")

        if root != self:
            url = f"{url}#{self.slug}"  # append hash with current answer id

        return url

    def get_root_answer(self) -> "Answer":
        ancestors = self.ancestors()
        if ancestors.count():
            return ancestors[0]

        return self

    def get_first_level_descendants(self) -> "AnswerQuerySet":
        return self.descendants().filter(parent=self.id)

    @property
    def is_root(self) -> bool:
        """Can be used to determine homework answer"""
        return self.parent is None

    @property
    def is_editable(self) -> bool:
        """May be edited by user"""
        return timezone.now() - self.created < settings.HOMEWORK_ANSWER_EDIT_PERIOD

    def is_author_of_root_answer(self, user: "User") -> bool:
        return self.get_root_answer().author == user

    def get_comments(self) -> "AnswerQuerySet":
        return self.get_first_level_descendants().order_by("created")

    def get_limited_comments_for_user_by_crosschecks(self, user: "User") -> "AnswerQuerySet":
        queryset = self.get_comments()

        if not self.is_root or not self.is_author_of_root_answer(user):
            return queryset

        students_should_check_my_answer = self.answercrosscheck_set.values_list("checker_id", flat=True)
        answers_from_students_that_should_check_my_answer = queryset.filter(author_id__in=students_should_check_my_answer).values_list("pk", flat=True)

        if not answers_from_students_that_should_check_my_answer.exists():  # no crosschecked answers, so return default queryset to avoid extra queries
            return queryset

        crosscheck_count = user.answercrosscheck_set.count_for_question(self.question)

        if crosscheck_count["total"] > crosscheck_count["checked"]:
            allowed_ids = answers_from_students_that_should_check_my_answer[
                : crosscheck_count["checked"]
            ]  # we show as many answers as the user has made checks
            ids_to_exclude = set(answers_from_students_that_should_check_my_answer) - set(
                allowed_ids
            )  # exclude answers from crosscheck that not in allowed_ids

            return queryset.exclude(pk__in=ids_to_exclude)

        return queryset
