from typing import Optional

import contextlib
import textwrap
import uuid
from django.conf import settings
from django.db.models import Count, Index, Q, UniqueConstraint
from django.db.models.query_utils import FilteredRelation
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from tree_queries.models import TreeNode, TreeQuerySet
from urllib.parse import urljoin

from app.markdown import markdownify, remove_html
from app.models import DefaultQuerySet, TimestampedModel, models
from orders.models import Order


class Question(TimestampedModel):
    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    courses = models.ManyToManyField('products.Course')
    name = models.CharField(_('Name'), max_length=256)

    text = MarkdownxField()

    class Meta:
        verbose_name = _('Homework')
        verbose_name_plural = _('Homeworks')
        permissions = [
            ('see_all_questions', _('May see questions for all homeworks')),
        ]

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, f'homework/questions/{self.slug}/')

    def dispatch_crosscheck(self, *args, **kwargs):
        from homework.services import QuestionCrossCheckDispatcher
        dispatcher = QuestionCrossCheckDispatcher(question=self, *args, **kwargs)

        return dispatcher()


class AnswerQuerySet(TreeQuerySet):
    def for_viewset(self):
        return self.with_tree_fields().select_related('author', 'question')

    def accessed_by(self, user):
        return self.with_tree_fields().annotate(
            access_log_entries_for_this_user=FilteredRelation('answeraccesslogentry', condition=Q(answeraccesslogentry__user=user)),
        ).filter(Q(author=user) | Q(access_log_entries_for_this_user__user=user))

    def for_user(self, user):
        accessed_answers = self.accessed_by(user)

        roots_of_accessed = [str(answer.tree_path[0]) for answer in accessed_answers.iterator()]

        if len(roots_of_accessed) > 0:
            return self.with_tree_fields().extra(where=[f'tree_path[1] in ({",".join(roots_of_accessed)})'])
        else:
            return self.none()

    def with_crosscheck_count(self):
        return self.annotate(crosscheck_count=Count('answercrosscheck'))

    def root_only(self):
        return self.filter(parent__isnull=True)


class Answer(TreeNode):
    objects: AnswerQuerySet = AnswerQuerySet.as_manager()

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

    def get_root_answer(self):
        ancesorts = self.ancestors()
        if ancesorts.count():
            return ancesorts[0]

        return self

    def get_absolute_url(self):
        root = self.get_root_answer()

        url = urljoin(settings.FRONTEND_URL, f'homework/answers/{root.slug}/')

        if root != self:
            url = f'{url}#{self.slug}'  # append hash with current answer id

        return url

    def get_purchased_course(self):
        latest_purchase = Order.objects.paid().filter(user=self.author, course__in=self.question.courses.all()).order_by('-paid').first()

        if latest_purchase:
            return latest_purchase.course

    def get_first_level_descendants(self):
        return self.descendants().filter(parent=self.id)

    def __str__(self) -> str:
        text = remove_html(markdownify(self.text))
        return textwrap.shorten(text, width=40)


class AnswerAccessLogEntryQuerySet(DefaultQuerySet):
    def get_for_user_and_answer(self, answer, user) -> Optional[models.Model]:
        with contextlib.suppress(self.model.DoesNotExist):
            return self.get(answer=answer, user=user)


class AnswerAccessLogEntry(TimestampedModel):
    objects: AnswerAccessLogEntryQuerySet = AnswerAccessLogEntryQuerySet.as_manager()

    answer = models.ForeignKey('homework.Answer', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            Index(fields=['answer', 'user']),
        ]
        constraints = [
            UniqueConstraint(fields=['answer', 'user'], name='unique_user_and_answer'),
        ]


class AnswerCrossCheck(TimestampedModel):
    answer = models.ForeignKey('homework.Answer', on_delete=models.CASCADE)
    checker = models.ForeignKey('users.User', on_delete=models.CASCADE)

    class Meta:
        indexes = [
            Index(fields=['answer', 'checker']),
        ]

        constraints = [
            UniqueConstraint(fields=['answer', 'checker'], name='unique_checker_and_answer'),
        ]

    def is_checked(self):
        return self.answer.descendants().filter(author=self.checker).exists()
