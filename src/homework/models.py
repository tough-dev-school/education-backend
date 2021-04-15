import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from urllib.parse import urljoin

from app.models import TimestampedModel, models


class Question(TimestampedModel):
    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    course = models.ForeignKey('products.Course', on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=256)

    text = MarkdownxField()

    class Meta:
        verbose_name = _('Homework')
        verbose_name_plural = _('Homeworks')

    def get_absolute_url(self):
        return urljoin(settings.FRONTEND_URL, f'/homework/questions/{self.slug}/')


class Answer(TimestampedModel):
    slug = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4)
    question = models.ForeignKey('homework.Question', on_delete=models.CASCADE)
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)

    text = MarkdownxField()

    class Meta:
        verbose_name = _('Homework answer')
        verbose_name_plural = _('Homework answers')
