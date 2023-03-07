import textwrap
from typing import Optional
from urllib.parse import urljoin
import uuid

from markdownx.models import MarkdownxField
from tree_queries.models import TreeNode
from tree_queries.query import TreeQuerySet

from django.conf import settings
from django.db.models import Count
from django.db.models import Q
from django.db.models.query_utils import FilteredRelation
from django.utils.translation import gettext_lazy as _

from app.markdown import markdownify
from app.markdown import remove_html
from app.models import models
from orders.models import Order
from products.models import Course
from users.models import User


class AnswerQuerySet(TreeQuerySet):
    def for_viewset(self) -> "AnswerQuerySet":
        return self.with_tree_fields().select_related("author", "question")

    def accessed_by(self, user) -> "AnswerQuerySet":
        return (
            self.with_tree_fields()
            .annotate(
                access_log_entries_for_this_user=FilteredRelation("answeraccesslogentry", condition=Q(answeraccesslogentry__user=user)),
            )
            .filter(
                Q(author=user) | Q(access_log_entries_for_this_user__user=user),
            )
        )

    def allowed_for_user(self, user: User) -> "AnswerQuerySet":
        """
        Return all child answers of allowed to access answers

        The answer is allowed to access for user:
            1. If user has permissions 'homework.see_all_answers': all answers without restrictions
            2. All other users: answers where user is author or any other answers that have ever been accessed
            by given user
        """
        if user.has_perm("homework.see_all_answers"):
            return self

        accessed_answers = self.accessed_by(user)

        roots_of_accessed_answers = [str(answer.tree_path[0]) for answer in accessed_answers.iterator()]

        if len(roots_of_accessed_answers) > 0:
            return self.with_tree_fields().extra(where=[f'tree_path[1] in ({",".join(roots_of_accessed_answers)})'])
        else:
            return self.none()

    def with_crosscheck_count(self) -> "AnswerQuerySet":
        return self.annotate(crosscheck_count=Count("answercrosscheck"))

    def root_only(self) -> "AnswerQuerySet":
        return self.filter(parent__isnull=True)

    def with_children_count(self) -> "AnswerQuerySet":
        return self.annotate(children_count=Count("children"))


class Answer(TreeNode):
    objects = models.Manager.from_queryset(AnswerQuerySet)()

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    question = models.ForeignKey("homework.Question", on_delete=models.CASCADE)
    author = models.ForeignKey("users.User", on_delete=models.CASCADE)
    do_not_crosscheck = models.BooleanField(_("Exclude from cross-checking"), default=False)

    text = MarkdownxField()

    class Meta:
        verbose_name = _("Homework answer")
        verbose_name_plural = _("Homework answers")
        ordering = ["created"]
        permissions = [
            ("see_all_answers", _("May see answers from every user")),
        ]

    def get_root_answer(self) -> "Answer":
        ancesorts = self.ancestors()
        if ancesorts.count():
            return ancesorts[0]

        return self

    def get_absolute_url(self) -> str:
        root = self.get_root_answer()

        url = urljoin(settings.FRONTEND_URL, f"homework/answers/{root.slug}/")

        if root != self:
            url = f"{url}#{self.slug}"  # append hash with current answer id

        return url

    def get_purchased_course(self) -> Optional[Course]:
        latest_purchase = Order.objects.paid().filter(user=self.author, course__in=self.question.courses.all()).order_by("-paid").first()

        if latest_purchase:
            return latest_purchase.course

        return None

    def get_first_level_descendants(self) -> "AnswerQuerySet":
        return self.descendants().filter(parent=self.id)

    def __str__(self) -> str:
        text = remove_html(markdownify(self.text))
        return textwrap.shorten(text, width=40)
