from typing import Optional

import contextlib
import uuid
from django.conf import settings
from django.db.models import Index, Q, UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from tree_queries.models import TreeNode
from urllib.parse import urljoin

from app.models import DefaultQuerySet, TimestampedModel, models


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


class AnswerQuerySet(DefaultQuerySet):
    def for_user(self, user):
        return self.filter(
            Q(author=user) | Q(parent__author=user) | Q(answeraccesslogentry__user=user),
        )


class Answer(TreeNode):
    objects: AnswerQuerySet = AnswerQuerySet.as_manager()

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(null=True, blank=True, db_index=True)

    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    question = models.ForeignKey('homework.Question', on_delete=models.CASCADE)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)

    text = MarkdownxField()

    class Meta:
        verbose_name = _('Homework answer')
        verbose_name_plural = _('Homework answers')
        ordering = ['created']
        permissions = [
            ('see_all_answers', _('May see answers from every user')),
        ]

    def save(self, *args, **kwargs):
        if self.pk:
            self.modified = timezone.now()

        return super().save(*args, **kwargs)


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
