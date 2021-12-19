from typing import Optional

import textwrap
import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from tree_queries.models import TreeNode
from urllib.parse import urljoin

from app.markdown import markdownify, remove_html
from app.models import models
from orders.models import Order
from products.models import Course
from homework.querysets import AnswerQuerySet


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

