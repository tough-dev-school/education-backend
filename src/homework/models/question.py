import uuid
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
from urllib.parse import urljoin

from app.models import TimestampedModel, models

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

    def get_absolute_url(self) -> str:
        return urljoin(settings.FRONTEND_URL, f'homework/questions/{self.slug}/')

    def dispatch_crosscheck(self, **kwargs) -> int:
        from homework.services import QuestionCrossCheckDispatcher
        dispatcher = QuestionCrossCheckDispatcher(question=self, **kwargs)

        return dispatcher()
