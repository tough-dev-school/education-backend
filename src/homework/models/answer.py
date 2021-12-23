from typing import Optional

import textwrap
import uuid
from django.conf import settings
from django.db.models import Count, Q, QuerySet
from django.db.models.query_utils import FilteredRelation
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from tree_queries.models import TreeNode, TreeQuerySet
from urllib.parse import urljoin

from app.markdown import markdownify, remove_html
from app.models import models
from orders.models import Order
from products.models import Course


class AnswerQuerySet(TreeQuerySet):
    def for_viewset(self) -> QuerySet['Answer']:
        return self.with_tree_fields().select_related('author', 'question')

    def accessed_by(self, user) -> QuerySet['Answer']:
        return self.with_tree_fields().annotate(
            access_log_entries_for_this_user=FilteredRelation(
                'answeraccesslogentry',
                condition=Q(answeraccesslogentry__user=user)),
        ).filter(
            Q(author=user) | Q(access_log_entries_for_this_user__user=user),
        )

    def for_user(self, user):
        """
        Return all child answers of any
        answers that have ever been accessed by given user
        """
        accessed_answers = self.accessed_by(user)

        roots_of_accessed_answers = [
            str(answer.tree_path[0]) for answer in accessed_answers.iterator()
        ]

        if len(roots_of_accessed_answers) > 0:
            return self.with_tree_fields().extra(where=[f'tree_path[1] in ({",".join(roots_of_accessed_answers)})'])
        else:
            return self.none()

    def with_crosscheck_count(self):
        return self.annotate(crosscheck_count=Count('answercrosscheck'))

    def root_only(self):
        return self.filter(parent__isnull=True)


class Answer(TreeNode):
    objects = models.Manager.from_queryset(AnswerQuerySet)()

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True, db_index=True)

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    question = models.ForeignKey('homework.Question', on_delete=models.CASCADE)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    do_not_crosscheck = models.BooleanField(_('Exclude from cross-checking'), default=False)

    text = MarkdownxField()

    class Meta:
        verbose_name = _('Homework answer')
        verbose_name_plural = _('Homework answers')
        ordering = ['created']
        permissions = [
            ('see_all_answers', _('May see answers from every user')),
        ]

    def get_root_answer(self) -> 'Answer':
        ancesorts = self.ancestors()
        if ancesorts.count():
            return ancesorts[0]

        return self

    def get_absolute_url(self) -> str:
        root = self.get_root_answer()

        url = urljoin(settings.FRONTEND_URL, f'homework/answers/{root.slug}/')

        if root != self:
            url = f'{url}#{self.slug}'  # append hash with current answer id

        return url

    def get_purchased_course(self) -> Optional[Course]:
        latest_purchase = Order.objects.paid().filter(user=self.author, course__in=self.question.courses.all()).order_by('-paid').first()

        if latest_purchase:
            return latest_purchase.course

        return None

    def get_first_level_descendants(self):
        return self.descendants().filter(parent=self.id)

    def __str__(self) -> str:
        text = remove_html(markdownify(self.text))
        return textwrap.shorten(text, width=40)
